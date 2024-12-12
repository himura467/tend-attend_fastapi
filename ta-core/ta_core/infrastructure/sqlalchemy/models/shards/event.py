from datetime import datetime

from sqlalchemy.dialects.mysql import BOOLEAN, DATETIME, ENUM, JSON, SMALLINT, VARCHAR
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

from ta_core.domain.entities.event import Event as EventEntity
from ta_core.domain.entities.event import EventAttendance as EventAttendanceEntity
from ta_core.domain.entities.event import Recurrence as RecurrenceEntity
from ta_core.domain.entities.event import RecurrenceRule as RecurrenceRuleEntity
from ta_core.features.event import AttendanceStatus, Frequency, Weekday
from ta_core.infrastructure.sqlalchemy.models.shards.base import (
    AbstractShardDynamicBase,
    AbstractShardStaticBase,
)


class RecurrenceRule(AbstractShardStaticBase):
    freq: Mapped[Frequency] = mapped_column(
        ENUM(Frequency), nullable=False, comment="FREQ"
    )
    until: Mapped[datetime | None] = mapped_column(
        DATETIME, nullable=True, comment="UNTIL"
    )
    count: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True), nullable=True, comment="COUNT"
    )
    interval: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True), nullable=False, comment="INTERVAL"
    )
    bysecond: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYSECOND"
    )
    byminute: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYMINUTE"
    )
    byhour: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYHOUR"
    )
    byday: Mapped[list[list[int | Weekday]] | None] = mapped_column(
        JSON, nullable=True, comment="BYDAY"
    )
    bymonthday: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYMONTHDAY"
    )
    byyearday: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYYEARDAY"
    )
    byweekno: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYWEEKNO"
    )
    bymonth: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYMONTH"
    )
    bysetpos: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True, comment="BYSETPOS"
    )
    wkst: Mapped[Weekday] = mapped_column(ENUM(Weekday), nullable=False, comment="WKST")

    def to_entity(self) -> RecurrenceRuleEntity:
        return RecurrenceRuleEntity(
            entity_id=self.id,
            user_id=self.user_id,
            freq=self.freq,
            until=self.until,
            count=self.count,
            interval=self.interval,
            bysecond=self.bysecond,
            byminute=self.byminute,
            byhour=self.byhour,
            byday=self.byday,
            bymonthday=self.bymonthday,
            byyearday=self.byyearday,
            byweekno=self.byweekno,
            bymonth=self.bymonth,
            bysetpos=self.bysetpos,
            wkst=self.wkst,
        )

    @classmethod
    def from_entity(cls, entity: RecurrenceRuleEntity) -> "RecurrenceRule":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            freq=entity.freq,
            until=entity.until,
            count=entity.count,
            interval=entity.interval,
            bysecond=entity.bysecond,
            byminute=entity.byminute,
            byhour=entity.byhour,
            byday=entity.byday,
            bymonthday=entity.bymonthday,
            byyearday=entity.byyearday,
            byweekno=entity.byweekno,
            bymonth=entity.bymonth,
            bysetpos=entity.bysetpos,
            wkst=entity.wkst,
        )


class Recurrence(AbstractShardStaticBase):
    rrule_id: Mapped[str] = mapped_column(
        VARCHAR(36),
        ForeignKey("recurrence_rule.id", ondelete="RESTRICT"),
        nullable=False,
    )
    rrule: Mapped[RecurrenceRule] = relationship(uselist=False)
    rdate: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="RDATE")
    exdate: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="EXDATE")

    def to_entity(self) -> RecurrenceEntity:
        rrule = self.rrule.to_entity()

        return RecurrenceEntity(
            entity_id=self.id,
            user_id=self.user_id,
            rrule_id=self.rrule_id,
            rrule=rrule,
            rdate=self.rdate,
            exdate=self.exdate,
        )

    @classmethod
    def from_entity(cls, entity: RecurrenceEntity) -> "Recurrence":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            rrule_id=entity.rrule_id,
            rdate=entity.rdate,
            exdate=entity.exdate,
        )


class Event(AbstractShardDynamicBase):
    summary: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, nullable=False, comment="Summary"
    )
    location: Mapped[str | None] = mapped_column(
        VARCHAR(64), nullable=True, comment="Location"
    )
    start: Mapped[datetime] = mapped_column(DATETIME, nullable=False, comment="Start")
    end: Mapped[datetime] = mapped_column(DATETIME, nullable=False, comment="End")
    is_all_day: Mapped[bool] = mapped_column(
        BOOLEAN, nullable=False, comment="Is All Day"
    )
    recurrence_id: Mapped[str | None] = mapped_column(
        VARCHAR(36),
        ForeignKey("recurrence.id", ondelete="RESTRICT"),
        nullable=True,
    )
    timezone: Mapped[str] = mapped_column(
        VARCHAR(64), nullable=False, comment="Timezone"
    )
    recurrence: Mapped[Recurrence | None] = relationship(uselist=False)

    def to_entity(self) -> EventEntity:
        try:
            recurrence = self.recurrence.to_entity() if self.recurrence else None
        except StatementError:
            recurrence = None

        return EventEntity(
            entity_id=self.id,
            user_id=self.user_id,
            summary=self.summary,
            location=self.location,
            start=self.start,
            end=self.end,
            is_all_day=self.is_all_day,
            recurrence_id=self.recurrence_id,
            timezone=self.timezone,
            recurrence=recurrence,
        )

    @classmethod
    def from_entity(cls, entity: EventEntity) -> "Event":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            summary=entity.summary,
            location=entity.location,
            start=entity.start,
            end=entity.end,
            is_all_day=entity.is_all_day,
            recurrence_id=entity.recurrence_id,
            timezone=entity.timezone,
        )


class EventAttendance(AbstractShardDynamicBase):
    event_id: Mapped[str] = mapped_column(
        VARCHAR(36),
        nullable=False,
        comment="Event ID",
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        ENUM(AttendanceStatus), nullable=False, comment="Attendance Status"
    )

    def to_entity(self) -> EventAttendanceEntity:
        return EventAttendanceEntity(
            entity_id=self.id,
            user_id=self.user_id,
            event_id=self.event_id,
            status=self.status,
        )

    @classmethod
    def from_entity(cls, entity: EventAttendanceEntity) -> "EventAttendance":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            event_id=entity.event_id,
            status=entity.status,
        )
