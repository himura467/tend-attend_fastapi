from datetime import date, datetime

from sqlalchemy.dialects.mysql import DATE, DATETIME, ENUM, JSON, SMALLINT, VARCHAR
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.schema import ForeignKey

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
from ta_core.infrastructure.sqlalchemy.models.shards.base import (
    AbstractShardDynamicBase,
    AbstractShardStaticBase,
)


class AllDayRecurrenceRule(AbstractShardStaticBase):
    freq: Mapped[Frequency] = mapped_column(
        ENUM(Frequency), nullable=False, comment="FREQ"
    )
    until: Mapped[date | None] = mapped_column(DATE, nullable=True, comment="UNTIL")
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

    def to_entity(self) -> AllDayRecurrenceRuleEntity:
        return AllDayRecurrenceRuleEntity(
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
    def from_entity(cls, entity: AllDayRecurrenceRuleEntity) -> "AllDayRecurrenceRule":
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


class TimedRecurrenceRule(AbstractShardStaticBase):
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

    def to_entity(self) -> TimedRecurrenceRuleEntity:
        return TimedRecurrenceRuleEntity(
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
    def from_entity(cls, entity: TimedRecurrenceRuleEntity) -> "TimedRecurrenceRule":
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


class AllDayRecurrence(AbstractShardStaticBase):
    rrule_id: Mapped[str] = mapped_column(
        VARCHAR(36),
        ForeignKey("all_day_recurrence_rule.id", ondelete="RESTRICT"),
        nullable=False,
    )
    rrule: Mapped[AllDayRecurrenceRule] = relationship(uselist=False)
    rdate: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="RDATE")
    exdate: Mapped[list[str]] = mapped_column(JSON, nullable=False, comment="EXDATE")

    def to_entity(self) -> AllDayRecurrenceEntity:
        return AllDayRecurrenceEntity(
            entity_id=self.id,
            user_id=self.user_id,
            rrule_id=self.rrule_id,
            rdate=self.rdate,
            exdate=self.exdate,
        )

    @classmethod
    def from_entity(cls, entity: AllDayRecurrenceEntity) -> "AllDayRecurrence":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            rrule_id=entity.rrule_id,
            rdate=entity.rdate,
            exdate=entity.exdate,
        )


class TimedRecurrence(AbstractShardStaticBase):
    rrule_id: Mapped[str] = mapped_column(
        VARCHAR(36),
        ForeignKey("timed_recurrence_rule.id", ondelete="RESTRICT"),
        nullable=False,
    )
    rrule: Mapped[TimedRecurrenceRule] = relationship(uselist=False)

    def to_entity(self) -> TimedRecurrenceEntity:
        return TimedRecurrenceEntity(
            entity_id=self.id,
            user_id=self.user_id,
            rrule_id=self.rrule_id,
        )

    @classmethod
    def from_entity(cls, entity: TimedRecurrenceEntity) -> "TimedRecurrence":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            rrule_id=entity.rrule_id,
        )


class AllDayEvent(AbstractShardDynamicBase):
    summary: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, nullable=False, comment="Summary"
    )
    location: Mapped[str | None] = mapped_column(
        VARCHAR(64), nullable=True, comment="Location"
    )
    start: Mapped[date] = mapped_column(DATE, nullable=False, comment="Start Date")
    end: Mapped[date] = mapped_column(DATE, nullable=False, comment="End Date")
    recurrence_id: Mapped[str | None] = mapped_column(
        VARCHAR(36),
        ForeignKey("all_day_recurrence.id", ondelete="RESTRICT"),
        nullable=True,
    )
    recurrence: Mapped[AllDayRecurrence | None] = relationship(uselist=False)

    def to_entity(self) -> AllDayEventEntity:
        return AllDayEventEntity(
            entity_id=self.id,
            user_id=self.user_id,
            summary=self.summary,
            location=self.location,
            start=self.start,
            end=self.end,
            recurrence_id=self.recurrence_id,
        )

    @classmethod
    def from_entity(cls, entity: AllDayEventEntity) -> "AllDayEvent":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            summary=entity.summary,
            location=entity.location,
            start=entity.start,
            end=entity.end,
            recurrence_id=entity.recurrence_id,
        )


class TimedEvent(AbstractShardDynamicBase):
    summary: Mapped[str] = mapped_column(
        VARCHAR(64), unique=True, nullable=False, comment="Summary"
    )
    location: Mapped[str | None] = mapped_column(
        VARCHAR(64), nullable=True, comment="Location"
    )
    start: Mapped[datetime] = mapped_column(
        DATETIME, nullable=False, comment="Start Date-Time"
    )
    end: Mapped[datetime] = mapped_column(
        DATETIME, nullable=False, comment="End Date-Time"
    )
    recurrence_id: Mapped[str | None] = mapped_column(
        VARCHAR(36),
        ForeignKey("timed_recurrence.id", ondelete="RESTRICT"),
        nullable=True,
    )
    recurrence: Mapped[TimedRecurrence | None] = relationship(uselist=False)

    def to_entity(self) -> TimedEventEntity:
        return TimedEventEntity(
            entity_id=self.id,
            user_id=self.user_id,
            summary=self.summary,
            location=self.location,
            start=self.start,
            end=self.end,
            recurrence_id=self.recurrence_id,
        )

    @classmethod
    def from_entity(cls, entity: TimedEventEntity) -> "TimedEvent":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            summary=entity.summary,
            location=entity.location,
            start=entity.start,
            end=entity.end,
            recurrence_id=entity.recurrence_id,
        )
