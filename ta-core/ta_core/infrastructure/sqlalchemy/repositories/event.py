from datetime import datetime

from sqlalchemy.orm.strategy_options import joinedload
from sqlalchemy.sql import select

from ta_core.domain.entities.event import Event as EventEntity
from ta_core.domain.entities.event import EventAttendance as EventAttendanceEntity
from ta_core.domain.entities.event import Recurrence as RecurrenceEntity
from ta_core.domain.entities.event import RecurrenceRule as RecurrenceRuleEntity
from ta_core.features.event import AttendanceStatus, Frequency, Weekday
from ta_core.infrastructure.sqlalchemy.models.shards.event import (
    Event,
    EventAttendance,
    Recurrence,
    RecurrenceRule,
)
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository


class RecurrenceRuleRepository(
    AbstractRepository[RecurrenceRuleEntity, RecurrenceRule],
):
    @property
    def _model(self) -> type[RecurrenceRule]:
        return RecurrenceRule

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
    ) -> RecurrenceRuleEntity | None:
        recurrence_rule = RecurrenceRuleEntity(
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
        return await self.create_async(recurrence_rule)


class RecurrenceRepository(
    AbstractRepository[RecurrenceEntity, Recurrence],
):
    @property
    def _model(self) -> type[Recurrence]:
        return Recurrence

    async def create_recurrence_async(
        self,
        entity_id: str,
        user_id: int,
        rrule_id: str,
        rrule: RecurrenceRuleEntity,
        rdate: list[str],
        exdate: list[str],
    ) -> RecurrenceEntity | None:
        recurrence = RecurrenceEntity(
            entity_id=entity_id,
            user_id=user_id,
            rrule_id=rrule_id,
            rrule=rrule,
            rdate=rdate,
            exdate=exdate,
        )
        return await self.create_async(recurrence)


class EventRepository(AbstractRepository[EventEntity, Event]):
    @property
    def _model(self) -> type[Event]:
        return Event

    async def create_event_async(
        self,
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: datetime,
        end: datetime,
        is_all_day: bool,
        recurrence_id: str | None,
        timezone: str,
    ) -> EventEntity | None:
        event = EventEntity(
            entity_id=entity_id,
            user_id=user_id,
            summary=summary,
            location=location,
            start=start,
            end=end,
            is_all_day=is_all_day,
            recurrence_id=recurrence_id,
            timezone=timezone,
        )
        return await self.create_async(event)

    async def read_with_recurrence_by_user_id_async(
        self, user_id: int
    ) -> tuple[EventEntity, ...]:
        stmt = (
            select(self._model)
            .where(self._model.user_id == user_id)
            .options(joinedload(Event.recurrence).joinedload(Recurrence.rrule))
        )
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.unique().scalars().all())


class EventAttendanceRepository(
    AbstractRepository[EventAttendanceEntity, EventAttendance],
):
    @property
    def _model(self) -> type[EventAttendance]:
        return EventAttendance

    async def create_event_attendance_async(
        self,
        entity_id: str,
        user_id: int,
        event_id: str,
    ) -> EventAttendanceEntity | None:
        event_attendance = EventAttendanceEntity(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            status=AttendanceStatus.UNDETERMINED,
        )
        return await self.create_async(event_attendance)
