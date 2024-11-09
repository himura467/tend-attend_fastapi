from abc import abstractmethod
from datetime import date, datetime
from typing import Any, Generic, TypeVar

from ta_core.domain.entities.event import AllDayEvent as AllDayEventEntity
from ta_core.domain.entities.event import AllDayRecurrence as AllDayRecurrenceEntity
from ta_core.domain.entities.event import (
    AllDayRecurrenceRule as AllDayRecurrenceRuleEntity,
)
from ta_core.domain.entities.event import TimedEvent as TimedEventEntity
from ta_core.domain.entities.event import TimedRecurrence as TimedRecurrenceEntity
from ta_core.domain.entities.event import (
    TimedRecurrenceRule as TimedRecurrenceRuleEntity,
)
from ta_core.features.event import Frequency, Weekday
from ta_core.infrastructure.sqlalchemy.models.shards.event import (
    AllDayEvent,
    AllDayRecurrence,
    AllDayRecurrenceRule,
    TimedEvent,
    TimedRecurrence,
    TimedRecurrenceRule,
)
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository

TDatetime = TypeVar("TDatetime", date, datetime)


class AbstractRecurrenceRuleRepository(Generic[TDatetime]):
    @abstractmethod
    async def create_recurrence_rule_async(
        self,
        entity_id: str,
        user_id: int,
        freq: Frequency,
        until: TDatetime | None,
        count: int | None,
        interval: int,
        bysecond: list[int] | None,
        byminute: list[int] | None,
        byhour: list[int] | None,
        byday: list[list[int | Weekday]] | None,
        bymonthday: list[int] | None,
        byyearday: list[int] | None,
        byweekno: list[int] | None,
        bymonth: list[int] | None,
        bysetpos: list[int] | None,
        wkst: Weekday,
    ) -> Any:
        raise NotImplementedError()


class AllDayRecurrenceRuleRepository(
    AbstractRepository[AllDayRecurrenceRuleEntity, AllDayRecurrenceRule],
    AbstractRecurrenceRuleRepository[date],
):
    @property
    def _model(self) -> type[AllDayRecurrenceRule]:
        return AllDayRecurrenceRule

    async def create_recurrence_rule_async(
        self,
        entity_id: str,
        user_id: int,
        freq: Frequency,
        until: date | None,
        count: int | None,
        interval: int,
        bysecond: list[int] | None,
        byminute: list[int] | None,
        byhour: list[int] | None,
        byday: list[list[int | Weekday]] | None,
        bymonthday: list[int] | None,
        byyearday: list[int] | None,
        byweekno: list[int] | None,
        bymonth: list[int] | None,
        bysetpos: list[int] | None,
        wkst: Weekday,
    ) -> AllDayRecurrenceRuleEntity | None:
        all_day_recurrence_rule = AllDayRecurrenceRuleEntity(
            entity_id=entity_id,
            user_id=user_id,
            freq=freq,
            until=until,
            count=count,
            interval=interval,
            bysecond=bysecond,
            byminute=byminute,
            byhour=byhour,
            byday=byday,
            bymonthday=bymonthday,
            byyearday=byyearday,
            byweekno=byweekno,
            bymonth=bymonth,
            bysetpos=bysetpos,
            wkst=wkst,
        )
        return await self.create_async(all_day_recurrence_rule)


class TimedRecurrenceRuleRepository(
    AbstractRepository[TimedRecurrenceRuleEntity, TimedRecurrenceRule],
    AbstractRecurrenceRuleRepository[datetime],
):
    @property
    def _model(self) -> type[TimedRecurrenceRule]:
        return TimedRecurrenceRule

    async def create_recurrence_rule_async(
        self,
        entity_id: str,
        user_id: int,
        freq: Frequency,
        until: datetime | None,
        count: int | None,
        interval: int,
        bysecond: list[int] | None,
        byminute: list[int] | None,
        byhour: list[int] | None,
        byday: list[list[int | Weekday]] | None,
        bymonthday: list[int] | None,
        byyearday: list[int] | None,
        byweekno: list[int] | None,
        bymonth: list[int] | None,
        bysetpos: list[int] | None,
        wkst: Weekday,
    ) -> TimedRecurrenceRuleEntity | None:
        timed_recurrence_rule = TimedRecurrenceRuleEntity(
            entity_id=entity_id,
            user_id=user_id,
            freq=freq,
            until=until,
            count=count,
            interval=interval,
            bysecond=bysecond,
            byminute=byminute,
            byhour=byhour,
            byday=byday,
            bymonthday=bymonthday,
            byyearday=byyearday,
            byweekno=byweekno,
            bymonth=bymonth,
            bysetpos=bysetpos,
            wkst=wkst,
        )
        return await self.create_async(timed_recurrence_rule)


class AbstractRecurrenceRepository:
    @abstractmethod
    async def create_recurrence_async(
        self,
        entity_id: str,
        user_id: int,
        rrule_id: str,
        rdate: list[str] | None = None,
        exdate: list[str] | None = None,
    ) -> Any:
        raise NotImplementedError()


class AllDayRecurrenceRepository(
    AbstractRepository[AllDayRecurrenceEntity, AllDayRecurrence],
    AbstractRecurrenceRepository,
):
    @property
    def _model(self) -> type[AllDayRecurrence]:
        return AllDayRecurrence

    async def create_recurrence_async(
        self,
        entity_id: str,
        user_id: int,
        rrule_id: str,
        rdate: list[str] | None = None,
        exdate: list[str] | None = None,
    ) -> AllDayRecurrenceEntity | None:
        if rdate is None or exdate is None:
            raise ValueError("rdate and exdate must be provided")

        all_day_recurrence = AllDayRecurrenceEntity(
            entity_id=entity_id,
            user_id=user_id,
            rrule_id=rrule_id,
            rdate=rdate,
            exdate=exdate,
        )
        return await self.create_async(all_day_recurrence)


class TimedRecurrenceRepository(
    AbstractRepository[TimedRecurrenceEntity, TimedRecurrence],
    AbstractRecurrenceRepository,
):
    @property
    def _model(self) -> type[TimedRecurrence]:
        return TimedRecurrence

    async def create_recurrence_async(
        self,
        entity_id: str,
        user_id: int,
        rrule_id: str,
        rdate: list[str] | None = None,
        exdate: list[str] | None = None,
    ) -> TimedRecurrenceEntity | None:
        if rdate is not None or exdate is not None:
            raise ValueError("rdate and exdate must not be provided")

        timed_recurrence = TimedRecurrenceEntity(
            entity_id=entity_id, user_id=user_id, rrule_id=rrule_id
        )
        return await self.create_async(timed_recurrence)


class AbstractEventRepository(Generic[TDatetime]):
    @abstractmethod
    async def create_event_async(
        self,
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: TDatetime,
        end: TDatetime,
        recurrence_id: str | None,
    ) -> Any:
        raise NotImplementedError()


class AllDayEventRepository(
    AbstractRepository[AllDayEventEntity, AllDayEvent], AbstractEventRepository[date]
):
    @property
    def _model(self) -> type[AllDayEvent]:
        return AllDayEvent

    async def create_event_async(
        self,
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: date,
        end: date,
        recurrence_id: str | None,
    ) -> AllDayEventEntity | None:
        all_day_event = AllDayEventEntity(
            entity_id=entity_id,
            user_id=user_id,
            summary=summary,
            location=location,
            start=start,
            end=end,
            recurrence_id=recurrence_id,
        )
        return await self.create_async(all_day_event)


class TimedEventRepository(
    AbstractRepository[TimedEventEntity, TimedEvent], AbstractEventRepository[datetime]
):
    @property
    def _model(self) -> type[TimedEvent]:
        return TimedEvent

    async def create_event_async(
        self,
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: datetime,
        end: datetime,
        recurrence_id: str | None,
    ) -> TimedEventEntity | None:
        timed_event = TimedEventEntity(
            entity_id=entity_id,
            user_id=user_id,
            summary=summary,
            location=location,
            start=start,
            end=end,
            recurrence_id=recurrence_id,
        )
        return await self.create_async(timed_event)
