from datetime import datetime

from ta_core.domain.entities.base import IEntity
from ta_core.features.event import AttendanceAction, AttendanceState, Frequency, Weekday


class RecurrenceRule(IEntity):
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


class Recurrence(IEntity):
    def __init__(
        self,
        entity_id: str,
        user_id: int,
        rrule_id: str,
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
        entity_id: str,
        user_id: int,
        summary: str,
        location: str | None,
        start: datetime,
        end: datetime,
        is_all_day: bool,
        recurrence_id: str | None,
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


class EventAttendance(IEntity):
    def __init__(
        self,
        entity_id: str,
        user_id: int,
        event_id: str,
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
        entity_id: str,
        user_id: int,
        event_id: str,
        start: datetime,
        action: AttendanceAction,
    ) -> None:
        super().__init__(entity_id)
        self.user_id = user_id
        self.event_id = event_id
        self.start = start
        self.action = action

    def set_action(self, action: AttendanceAction) -> "EventAttendanceActionLog":
        return EventAttendanceActionLog(
            entity_id=self.id,
            user_id=self.user_id,
            event_id=self.event_id,
            start=self.start,
            action=action,
        )
