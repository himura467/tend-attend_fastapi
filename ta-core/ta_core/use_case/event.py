from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from ta_core.dtos.event import CreateEventResponse
from ta_core.error.error_code import ErrorCode
from ta_core.features.event import Event, Weekday
from ta_core.infrastructure.db.transaction import rollbackable
from ta_core.infrastructure.sqlalchemy.repositories.account import HostAccountRepository
from ta_core.infrastructure.sqlalchemy.repositories.event import (
    AbstractEventRepository,
    AbstractRecurrenceRepository,
    AbstractRecurrenceRuleRepository,
    AllDayEventRepository,
    AllDayRecurrenceRepository,
    AllDayRecurrenceRuleRepository,
    TimedEventRepository,
    TimedRecurrenceRepository,
    TimedRecurrenceRuleRepository,
)
from ta_core.use_case.unit_of_work_base import IUnitOfWork
from ta_core.utils.datetime import validate_date
from ta_core.utils.rfc5545_parser import parse_recurrence
from ta_core.utils.uuid import generate_uuid


def convert_tuple_to_list(t: tuple[int, ...] | None) -> list[int] | None:
    return list(t) if t is not None else None


def convert_byday_tuple_to_list(
    t: tuple[tuple[int, Weekday], ...] | None
) -> list[list[int | Weekday]] | None:
    return [list(i) for i in t] if t is not None else None


def convert_dates_to_str(dates: tuple[date, ...]) -> list[str]:
    return [d.isoformat() for d in dates]


@dataclass(frozen=True)
class EventUseCase:
    uow: IUnitOfWork

    @rollbackable
    async def create_event_async(
        self,
        host_id: str,
        summary: str,
        location: str | None,
        start_dt: datetime,
        end_dt: datetime,
        recurrence_list: list[str],
        is_all_day: bool,
    ) -> CreateEventResponse:
        host_account_repository = HostAccountRepository(self.uow)

        validate_date(is_all_day, start_dt)
        validate_date(is_all_day, end_dt)
        start = start_dt.date() if is_all_day else start_dt
        end = end_dt.date() if is_all_day else end_dt
        recurrence = (
            parse_recurrence(recurrence_list, is_all_day) if recurrence_list else None
        )
        event = Event(
            summary=summary,
            location=location,
            start=start,
            end=end,
            recurrence=recurrence,
        )

        host_account = await host_account_repository.read_by_id_or_none_async(host_id)
        if host_account is None:
            return CreateEventResponse(error_codes=(ErrorCode.HOST_ACCOUNT_NOT_FOUND,))
        if host_account.user_id is None:
            return CreateEventResponse(error_codes=(ErrorCode.ACCOUNT_DISABLED,))

        user_id = host_account.user_id

        recurrence_rule_repository: AbstractRecurrenceRuleRepository[Any]
        recurrence_repository: AbstractRecurrenceRepository
        event_repository: AbstractEventRepository[Any]

        if type(event.start) is date:
            recurrence_rule_repository = AllDayRecurrenceRuleRepository(self.uow)
            recurrence_repository = AllDayRecurrenceRepository(self.uow)
            event_repository = AllDayEventRepository(self.uow)
        elif type(event.start) is datetime:
            recurrence_rule_repository = TimedRecurrenceRuleRepository(self.uow)
            recurrence_repository = TimedRecurrenceRepository(self.uow)
            event_repository = TimedEventRepository(self.uow)
        else:
            raise ValueError("Invalid start type")

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
                    byday=convert_byday_tuple_to_list(event.recurrence.rrule.byday),
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
                rdate=convert_dates_to_str(event.recurrence.rdate),
                exdate=convert_dates_to_str(event.recurrence.exdate),
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
            recurrence_id=recurrence_id,
        )
        if event_entity is None:
            raise ValueError("Failed to create event")

        return CreateEventResponse(error_codes=())
