from datetime import datetime

from ta_core.domain.entities.base import IEntity
from ta_core.features.event import AttendanceAction, AttendanceState, Frequency, Weekday
from ta_core.utils.datetime import apply_timezone
from ta_core.utils.uuid import UUID


class RecurrenceRule(IEntity):
    def __init__(
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


class Recurrence(IEntity):
    def __init__(
        self,
        entity_id: UUID,
        user_id: int,
        rrule_id: UUID,
        rrule: RecurrenceRule,
        rdate: list[str],
        exdate: list[str],
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.rrule_id = rrule_id
        self.rrule = rrule
        self.rdate = rdate
        self.exdate = exdate


class Event(IEntity):
    def __init__(
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
        recurrence: Recurrence | None = None,
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.summary = summary
        self.location = location
        self.start = start
        self.end = end
        self.is_all_day = is_all_day
        self.recurrence_id = recurrence_id
        self.timezone = timezone
        self.recurrence = recurrence

    def is_attendable(self, start: datetime, current_time: datetime) -> bool:
        zoned_current = apply_timezone(current_time, self.timezone)
        zoned_start = apply_timezone(start, self.timezone)
        duration = self.end - self.start
        zoned_end = zoned_start + duration

        if self.is_all_day:
            return zoned_start <= zoned_current <= zoned_end

        zoned_open = max(
            zoned_start - duration,
            zoned_start.replace(hour=0, minute=0),
        )
        return zoned_open <= zoned_current <= zoned_end

    def is_leaveable(self, start: datetime, current_time: datetime) -> bool:
        zoned_current = apply_timezone(current_time, self.timezone)
        zoned_start = apply_timezone(start, self.timezone)
        duration = self.end - self.start
        zoned_end = zoned_start + duration

        if self.is_all_day:
            return zoned_start <= zoned_current <= zoned_end

        zoned_close = min(
            zoned_end + duration,
            zoned_end.replace(hour=23, minute=59),
        )
        return zoned_start <= zoned_current <= zoned_close


class EventAttendance(IEntity):
    def __init__(
        self,
        entity_id: UUID,
        user_id: int,
        event_id: UUID,
        start: datetime,
        state: AttendanceState,
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.event_id = event_id
        self.start = start
        self.state = state

    def set_state(self, state: AttendanceState) -> "EventAttendance":
        return EventAttendance(
            entity_id=self.id,
            user_id=self.user_id,
            event_id=self.event_id,
            start=self.start,
            state=state,
        )


class EventAttendanceActionLog(IEntity):
    def __init__(
        self,
        entity_id: UUID,
        user_id: int,
        event_id: UUID,
        start: datetime,
        action: AttendanceAction,
        acted_at: datetime,
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.event_id = event_id
        self.start = start
        self.action = action
        self.acted_at = acted_at
