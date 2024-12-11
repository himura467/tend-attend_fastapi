from dataclasses import dataclass
from datetime import date

from ta_core.domain.entities.event import Event as EventEntity
from ta_core.dtos.event import CreateEventResponse
from ta_core.dtos.event import Event as EventDto
from ta_core.dtos.event import EventWithId as EventWithIdDto
from ta_core.dtos.event import GetHostEventsResponse
from ta_core.error.error_code import ErrorCode
from ta_core.features.event import Event, Recurrence, RecurrenceRule, Weekday
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import HostAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.event import (
    EventRepository,
    RecurrenceRepository,
    RecurrenceRuleRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.datetime import validate_date
from ta_core.utils.rfc5545 import parse_recurrence, serialize_recurrence
from ta_core.utils.uuid import generate_uuid


def convert_tuple_to_list[T](tpl: tuple[T, ...] | None) -> list[T] | None:
    return list(tpl) if tpl is not None else None


def convert_list_to_tuple[T](lst: list[T] | None) -> tuple[T, ...] | None:
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
                id=event.id,
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
        host_id: str,
        event_dto: EventDto,
    ) -> CreateEventResponse:
        host_account_repository = HostAccountRepository(self.uow)
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

        host_account = await host_account_repository.read_by_id_or_none_async(host_id)
        if host_account is None:
            return CreateEventResponse(error_codes=(ErrorCode.HOST_ACCOUNT_NOT_FOUND,))
        if host_account.user_id is None:
            return CreateEventResponse(error_codes=(ErrorCode.ACCOUNT_DISABLED,))

        user_id = host_account.user_id

        recurrence_id: str | None
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
    async def get_host_events_async(self, host_id: str) -> GetHostEventsResponse:
        host_account_repository = HostAccountRepository(self.uow)
        event_repository = EventRepository(self.uow)

        host_account = await host_account_repository.read_by_id_or_none_async(host_id)
        if host_account is None:
            return GetHostEventsResponse(
                events=[], error_codes=(ErrorCode.HOST_ACCOUNT_NOT_FOUND,)
            )
        if host_account.user_id is None:
            return GetHostEventsResponse(
                events=[], error_codes=(ErrorCode.ACCOUNT_DISABLED,)
            )

        user_id = host_account.user_id

        events = await event_repository.read_with_recurrence_by_user_id_async(user_id)

        return GetHostEventsResponse(events=serialize_events(events), error_codes=())
