from dataclasses import dataclass
from datetime import date, datetime
from typing import TypeVar
from zoneinfo import ZoneInfo

from ta_core.domain.entities.event import Event as EventEntity
from ta_core.dtos.event import AttendEventResponse, CreateEventResponse
from ta_core.dtos.event import Event as EventDto
from ta_core.dtos.event import EventWithId as EventWithIdDto
from ta_core.dtos.event import (
    GetFollowingEventsResponse,
    GetGuestCurrentAttendanceStatusResponse,
    GetMyEventsResponse,
)
from ta_core.error.error_code import ErrorCode
from ta_core.features.event import (
    AttendanceAction,
    AttendanceState,
    Event,
    Recurrence,
    RecurrenceRule,
    Weekday,
)
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import UserAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.event import (
    EventAttendanceActionLogRepository,
    EventAttendanceRepository,
    EventRepository,
    RecurrenceRepository,
    RecurrenceRuleRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.datetime import validate_date
from ta_core.utils.rfc5545 import parse_recurrence, serialize_recurrence
from ta_core.utils.uuid import UUID, generate_uuid, str_to_uuid, uuid_to_str

T = TypeVar("T")


def convert_tuple_to_list(tpl: tuple[T, ...] | None) -> list[T] | None:
    return list(tpl) if tpl is not None else None


def convert_list_to_tuple(lst: list[T] | None) -> tuple[T, ...] | None:
    return tuple(lst) if lst is not None else None


def convert_byday_tuple_to_byday_list(
    tpl: tuple[tuple[int, Weekday], ...] | None
) -> list[list[int | Weekday]] | None:
    return [list(i) for i in tpl] if tpl is not None else None


def convert_byday_list_to_byday_tuple(
    lst: list[list[int | Weekday]] | None,
) -> tuple[tuple[int, Weekday], ...] | None:
    return (
        tuple((int(i[0]), Weekday(str(i[1]))) for i in lst) if lst is not None else None
    )


def convert_date_tuple_to_str_list(dates: tuple[date, ...]) -> list[str]:
    return [d.isoformat() for d in dates]


def convert_str_list_to_date_tuple(dates: list[str]) -> tuple[date, ...]:
    return tuple(date.fromisoformat(d) for d in dates)


def serialize_events(events: tuple[EventEntity, ...]) -> list[EventWithIdDto]:
    event_dto_list = []
    for event in events:
        recurrence: Recurrence | None = None
        if event.recurrence is not None:
            recurrence = Recurrence(
                rrule=RecurrenceRule(
                    freq=event.recurrence.rrule.freq,
                    until=event.recurrence.rrule.until,
                    count=event.recurrence.rrule.count,
                    interval=event.recurrence.rrule.interval,
                    bysecond=convert_list_to_tuple(event.recurrence.rrule.bysecond),
                    byminute=convert_list_to_tuple(event.recurrence.rrule.byminute),
                    byhour=convert_list_to_tuple(event.recurrence.rrule.byhour),
                    byday=convert_byday_list_to_byday_tuple(
                        event.recurrence.rrule.byday
                    ),
                    bymonthday=convert_list_to_tuple(event.recurrence.rrule.bymonthday),
                    byyearday=convert_list_to_tuple(event.recurrence.rrule.byyearday),
                    byweekno=convert_list_to_tuple(event.recurrence.rrule.byweekno),
                    bymonth=convert_list_to_tuple(event.recurrence.rrule.bymonth),
                    bysetpos=convert_list_to_tuple(event.recurrence.rrule.bysetpos),
                    wkst=event.recurrence.rrule.wkst,
                ),
                rdate=(
                    convert_str_list_to_date_tuple(event.recurrence.rdate)
                    if event.is_all_day
                    else tuple()
                ),
                exdate=(
                    convert_str_list_to_date_tuple(event.recurrence.exdate)
                    if event.is_all_day
                    else tuple()
                ),
            )
        event_dto_list.append(
            EventWithIdDto(
                id=uuid_to_str(event.id),
                summary=event.summary,
                location=event.location,
                start=event.start,
                end=event.end,
                is_all_day=event.is_all_day,
                recurrence_list=serialize_recurrence(recurrence, event.is_all_day),
                timezone=event.timezone,
            )
        )
    return event_dto_list


@dataclass(frozen=True)
class EventUseCase:
    uow: IUnitOfWork

    @rollbackable
    async def create_event_async(
        self,
        host_id: UUID,
        event_dto: EventDto,
    ) -> CreateEventResponse:
        user_account_repository = UserAccountRepository(self.uow)
        recurrence_rule_repository = RecurrenceRuleRepository(self.uow)
        recurrence_repository = RecurrenceRepository(self.uow)
        event_repository = EventRepository(self.uow)

        assert event_dto.start.tzname() == "UTC"
        assert event_dto.end.tzname() == "UTC"
        validate_date(
            is_all_day=event_dto.is_all_day,
            date_value=event_dto.start,
            timezone=event_dto.timezone,
        )
        validate_date(
            is_all_day=event_dto.is_all_day,
            date_value=event_dto.end,
            timezone=event_dto.timezone,
        )

        recurrence = parse_recurrence(event_dto.recurrence_list, event_dto.is_all_day)
        event = Event(
            summary=event_dto.summary,
            location=event_dto.location,
            start=event_dto.start,
            end=event_dto.end,
            timezone=event_dto.timezone,
            recurrence=recurrence,
            is_all_day=event_dto.is_all_day,
        )

        host = await user_account_repository.read_by_id_or_none_async(host_id)
        if host is None:
            return CreateEventResponse(error_codes=(ErrorCode.ACCOUNT_NOT_FOUND,))

        user_id = host.user_id

        recurrence_id: UUID | None
        if event.recurrence is None:
            recurrence_id = None
        else:
            recurrence_rule = (
                await recurrence_rule_repository.create_recurrence_rule_async(
                    entity_id=generate_uuid(),
                    user_id=user_id,
                    freq=event.recurrence.rrule.freq,
                    until=event.recurrence.rrule.until,
                    count=event.recurrence.rrule.count,
                    interval=event.recurrence.rrule.interval,
                    bysecond=convert_tuple_to_list(event.recurrence.rrule.bysecond),
                    byminute=convert_tuple_to_list(event.recurrence.rrule.byminute),
                    byhour=convert_tuple_to_list(event.recurrence.rrule.byhour),
                    byday=convert_byday_tuple_to_byday_list(
                        event.recurrence.rrule.byday
                    ),
                    bymonthday=convert_tuple_to_list(event.recurrence.rrule.bymonthday),
                    byyearday=convert_tuple_to_list(event.recurrence.rrule.byyearday),
                    byweekno=convert_tuple_to_list(event.recurrence.rrule.byweekno),
                    bymonth=convert_tuple_to_list(event.recurrence.rrule.bymonth),
                    bysetpos=convert_tuple_to_list(event.recurrence.rrule.bysetpos),
                    wkst=event.recurrence.rrule.wkst,
                )
            )
            if recurrence_rule is None:
                raise ValueError("Failed to create recurrence rule")

            recurrence_entity = await recurrence_repository.create_recurrence_async(
                entity_id=generate_uuid(),
                user_id=user_id,
                rrule_id=recurrence_rule.id,
                rrule=recurrence_rule,
                rdate=convert_date_tuple_to_str_list(event.recurrence.rdate),
                exdate=convert_date_tuple_to_str_list(event.recurrence.exdate),
            )
            if recurrence_entity is None:
                raise ValueError("Failed to create recurrence")

            recurrence_id = recurrence_entity.id

        event_entity = await event_repository.create_event_async(
            entity_id=generate_uuid(),
            user_id=user_id,
            summary=event.summary,
            location=event.location,
            start=event.start,
            end=event.end,
            is_all_day=event.is_all_day,
            recurrence_id=recurrence_id,
            timezone=event.timezone,
        )
        if event_entity is None:
            raise ValueError("Failed to create event")

        return CreateEventResponse(error_codes=())

    @rollbackable
    async def attend_event_async(
        self,
        guest_id: UUID,
        event_id_str: str,
        start: datetime,
        action: AttendanceAction,
    ) -> AttendEventResponse:
        user_account_repository = UserAccountRepository(self.uow)
        event_repository = EventRepository(self.uow)
        event_attendance_repository = EventAttendanceRepository(self.uow)
        event_attendance_action_log_repository = EventAttendanceActionLogRepository(
            self.uow
        )

        event_id = str_to_uuid(event_id_str)

        guest = await user_account_repository.read_by_id_or_none_async(guest_id)
        if guest is None:
            return AttendEventResponse(error_codes=(ErrorCode.ACCOUNT_NOT_FOUND,))

        user_id = guest.user_id

        event = await event_repository.read_by_id_or_none_async(event_id)
        if event is None:
            return AttendEventResponse(error_codes=(ErrorCode.EVENT_NOT_FOUND,))

        if action == AttendanceAction.ATTEND:
            if not event.is_attendable(start, datetime.now(ZoneInfo("UTC"))):
                return AttendEventResponse(
                    error_codes=(ErrorCode.EVENT_NOT_ATTENDABLE,)
                )

            await event_attendance_repository.create_or_update_event_attendance_async(
                entity_id=generate_uuid(),
                user_id=user_id,
                event_id=event.id,
                start=start,
                state=AttendanceState.PRESENT,
            )
        elif action == AttendanceAction.LEAVE:
            if not event.is_leaveable(start, datetime.now(ZoneInfo("UTC"))):
                return AttendEventResponse(error_codes=(ErrorCode.EVENT_NOT_LEAVEABLE,))

            await event_attendance_repository.create_or_update_event_attendance_async(
                entity_id=generate_uuid(),
                user_id=user_id,
                event_id=event.id,
                start=start,
                state=AttendanceState.EXCUSED_ABSENCE,
            )

        await event_attendance_action_log_repository.create_event_attendance_action_log_async(
            entity_id=generate_uuid(),
            user_id=user_id,
            event_id=event.id,
            start=start,
            action=action,
            acted_at=datetime.now(ZoneInfo("UTC")),
        )

        return AttendEventResponse(error_codes=())

    @rollbackable
    async def get_my_events_async(self, account_id: UUID) -> GetMyEventsResponse:
        user_account_repository = UserAccountRepository(self.uow)
        event_repository = EventRepository(self.uow)

        user_account = await user_account_repository.read_by_id_or_none_async(
            account_id
        )
        if user_account is None:
            return GetMyEventsResponse(
                events=[], error_codes=(ErrorCode.ACCOUNT_NOT_FOUND,)
            )

        user_id = user_account.user_id

        events = await event_repository.read_with_recurrence_by_user_ids_async(
            {user_id}
        )

        return GetMyEventsResponse(events=serialize_events(events), error_codes=())

    @rollbackable
    async def get_following_events_async(
        self, follower_id: UUID
    ) -> GetFollowingEventsResponse:
        user_account_repository = UserAccountRepository(self.uow)
        event_repository = EventRepository(self.uow)

        follower = await user_account_repository.read_by_id_or_none_async(follower_id)
        if follower is None:
            return GetFollowingEventsResponse(
                events=[], error_codes=(ErrorCode.ACCOUNT_NOT_FOUND,)
            )

        followees = await user_account_repository.read_by_ids_async(
            set(followee.id for followee in follower.followees)
        )

        user_ids = {followee.user_id for followee in followees} | {follower.user_id}

        events = await event_repository.read_with_recurrence_by_user_ids_async(user_ids)

        return GetFollowingEventsResponse(
            events=serialize_events(events), error_codes=()
        )

    @rollbackable
    async def get_guest_current_attendance_status_async(
        self, guest_id: UUID, event_id_str: str, start: datetime
    ) -> GetGuestCurrentAttendanceStatusResponse:
        user_account_repository = UserAccountRepository(self.uow)
        event_repository = EventRepository(self.uow)
        event_attendance_action_log_repository = EventAttendanceActionLogRepository(
            self.uow
        )

        event_id = str_to_uuid(event_id_str)

        guest = await user_account_repository.read_by_id_or_none_async(guest_id)
        if guest is None:
            return GetGuestCurrentAttendanceStatusResponse(
                attend=False, error_codes=(ErrorCode.ACCOUNT_NOT_FOUND,)
            )

        user_id = guest.user_id

        event = await event_repository.read_by_id_or_none_async(event_id)
        if event is None:
            return GetGuestCurrentAttendanceStatusResponse(
                attend=False, error_codes=(ErrorCode.EVENT_NOT_FOUND,)
            )

        event_attendance_action_log = await event_attendance_action_log_repository.read_latest_by_user_id_and_event_id_and_start_or_none_async(
            user_id=user_id, event_id=event_id, start=start
        )
        if event_attendance_action_log is None:
            return GetGuestCurrentAttendanceStatusResponse(attend=False, error_codes=())

        return GetGuestCurrentAttendanceStatusResponse(
            attend=event_attendance_action_log.action == AttendanceAction.ATTEND,
            error_codes=(),
        )
