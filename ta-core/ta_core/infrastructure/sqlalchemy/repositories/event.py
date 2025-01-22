from datetime import datetime

from sqlalchemy.orm.strategy_options import joinedload
from sqlalchemy.sql import select
from sqlalchemy.sql.functions import func

from ta_core.domain.entities.event import Event as EventEntity
from ta_core.domain.entities.event import EventAttendance as EventAttendanceEntity
from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)
from ta_core.domain.entities.event import Recurrence as RecurrenceEntity
from ta_core.domain.entities.event import RecurrenceRule as RecurrenceRuleEntity
from ta_core.features.event import AttendanceAction, AttendanceState, Frequency, Weekday
from ta_core.infrastructure.sqlalchemy.models.shards.event import (
    Event,
    EventAttendance,
    EventAttendanceActionLog,
    Recurrence,
    RecurrenceRule,
)
from ta_core.infrastructure.sqlalchemy.repositories.base import AbstractRepository
from ta_core.utils.uuid import UUID, uuid_to_bin


class RecurrenceRuleRepository(
    AbstractRepository[RecurrenceRuleEntity, RecurrenceRule],
):
    @property
    def _model(self) -> type[RecurrenceRule]:
        return RecurrenceRule

    async def create_recurrence_rule_async(
        self,
        entity_id: UUID,
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
        entity_id: UUID,
        user_id: int,
        rrule_id: UUID,
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
        entity_id: UUID,
        user_id: int,
        summary: str,
        location: str | None,
        start: datetime,
        end: datetime,
        is_all_day: bool,
        recurrence_id: UUID | None,
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

    async def read_with_recurrence_by_user_ids_async(
        self, user_ids: set[int]
    ) -> tuple[EventEntity, ...]:
        stmt = (
            select(self._model)
            .where(self._model.user_id.in_(user_ids))
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

    async def read_by_user_id_and_event_id_and_start_or_none_async(
        self, user_id: int, event_id: UUID, start: datetime
    ) -> EventAttendanceEntity | None:
        return await self.read_one_or_none_async(
            where=(
                self._model.user_id == user_id,
                self._model.event_id == uuid_to_bin(event_id),
                self._model.start == start,
            )
        )

    async def create_or_update_event_attendance_async(
        self,
        entity_id: UUID,
        user_id: int,
        event_id: UUID,
        start: datetime,
        state: AttendanceState,
    ) -> EventAttendanceEntity | None:
        existing_event_attendance = (
            await self.read_by_user_id_and_event_id_and_start_or_none_async(
                user_id=user_id, event_id=event_id, start=start
            )
        )
        if existing_event_attendance:
            updated_event_attendance = existing_event_attendance.set_state(state)
            return await self.update_async(updated_event_attendance)
        event_attendance = EventAttendanceEntity(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            start=start,
            state=state,
        )
        return await self.create_async(event_attendance)


class EventAttendanceActionLogRepository(
    AbstractRepository[EventAttendanceActionLogEntity, EventAttendanceActionLog],
):
    @property
    def _model(self) -> type[EventAttendanceActionLog]:
        return EventAttendanceActionLog

    async def create_event_attendance_action_log_async(
        self,
        entity_id: UUID,
        user_id: int,
        event_id: UUID,
        start: datetime,
        action: AttendanceAction,
        acted_at: datetime,
    ) -> EventAttendanceActionLogEntity | None:
        event_attendance_action_log = EventAttendanceActionLogEntity(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            start=start,
            action=action,
            acted_at=acted_at,
        )
        return await self.create_async(event_attendance_action_log)

    async def bulk_create_event_attendance_action_logs_async(
        self,
        event_attendance_action_logs: list[EventAttendanceActionLogEntity],
    ) -> list[EventAttendanceActionLogEntity] | None:
        return await self.bulk_create_async(event_attendance_action_logs)

    async def read_by_user_id_and_event_id_and_start_async(
        self, user_id: int, event_id: UUID, start: datetime
    ) -> tuple[EventAttendanceActionLogEntity, ...]:
        return await self.read_all_async(
            where=(
                self._model.user_id == user_id,
                self._model.event_id == uuid_to_bin(event_id),
                self._model.start == start,
            )
        )

    async def read_latest_by_user_id_and_event_id_and_start_or_none_async(
        self, user_id: int, event_id: UUID, start: datetime
    ) -> EventAttendanceActionLogEntity | None:
        event_attendance_action_logs = await self.read_order_by_limit_async(
            where=(
                self._model.user_id == user_id,
                self._model.event_id == uuid_to_bin(event_id),
                self._model.start == start,
            ),
            order_by=self._model.acted_at.desc(),
            limit=1,
        )
        return event_attendance_action_logs[0] if event_attendance_action_logs else None

    async def read_all_earliest_attend_async(
        self,
    ) -> tuple[EventAttendanceActionLogEntity, ...]:
        sub_query = (
            select(
                self._model.user_id,
                self._model.event_id,
                self._model.start,
                self._model.acted_at,
                func.row_number()
                .over(
                    partition_by=[
                        self._model.user_id,
                        self._model.event_id,
                        self._model.start,
                    ],
                    order_by=self._model.acted_at.asc(),
                )
                .label("rn"),
            )
            .where(self._model.action == "attend")
            .subquery()
        )
        stmt = (
            select(self._model)
            .join(
                sub_query,
                (self._model.user_id == sub_query.c.user_id)
                & (self._model.event_id == sub_query.c.event_id)
                & (self._model.start == sub_query.c.start)
                & (self._model.acted_at == sub_query.c.acted_at),
            )
            .where(sub_query.c.rn == 1)
        )
        result = await self._uow.execute_async(stmt)
        return tuple(record.to_entity() for record in result.scalars().all())

    async def delete_by_user_id_and_event_id_and_start_async(
        self, user_id: int, event_id: UUID, start: datetime
    ) -> None:
        await self.delete_all_async(
            where=(
                self._model.user_id == user_id,
                self._model.event_id == uuid_to_bin(event_id),
                self._model.start == start,
            )
        )
