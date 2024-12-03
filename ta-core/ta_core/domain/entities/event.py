from datetime import date, datetime

from ta_core.domain.entities.base import IEntity
from ta_core.features.event import Frequency, Weekday


class AllDayRecurrenceRule(IEntity):
    def __init__(
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
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.freq = freq
        self.until = until
        self.count = count
        self.interval = interval
        self.bysecond = bysecond
        self.byminute = byminute
        self.byhour = byhour
        self.byday = byday
        self.bymonthday = bymonthday
        self.byyearday = byyearday
        self.byweekno = byweekno
        self.bymonth = bymonth
        self.bysetpos = bysetpos
        self.wkst = wkst


class TimedRecurrenceRule(IEntity):
    def __init__(
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
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.freq = freq
        self.until = until
        self.count = count
        self.interval = interval
        self.bysecond = bysecond
        self.byminute = byminute
        self.byhour = byhour
        self.byday = byday
        self.bymonthday = bymonthday
        self.byyearday = byyearday
        self.byweekno = byweekno
        self.bymonth = bymonth
        self.bysetpos = bysetpos
        self.wkst = wkst


class AllDayRecurrence(IEntity):
    def __init__(
        self,
        entity_id: str,
        user_id: int,
        rrule_id: str,
        rrule: AllDayRecurrenceRule,
        rdate: list[str],
        exdate: list[str],
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.rrule_id = rrule_id
        self.rrule = rrule
        self.rdate = rdate
        self.exdate = exdate


class TimedRecurrence(IEntity):
    def __init__(
        self, entity_id: str, user_id: int, rrule_id: str, rrule: TimedRecurrenceRule
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.rrule_id = rrule_id
        self.rrule = rrule


class AllDayEvent(IEntity):
    def __init__(
        self,
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: date,
        end: date,
        recurrence_id: str | None,
        recurrence: AllDayRecurrence | None = None,
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.summary = summary
        self.location = location
        self.start = start
        self.end = end
        self.recurrence_id = recurrence_id
        self.recurrence = recurrence


class TimedEvent(IEntity):
    def __init__(
        self,
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: datetime,
        end: datetime,
        recurrence_id: str | None,
        recurrence: TimedRecurrence | None = None,
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.summary = summary
        self.location = location
        self.start = start
        self.end = end
        self.recurrence_id = recurrence_id
        self.recurrence = recurrence
