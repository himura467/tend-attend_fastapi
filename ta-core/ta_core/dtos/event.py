from datetime import date, datetime

from pydantic import BaseModel
from pydantic.fields import Field

from ta_core.dtos.base import BaseModelWithErrorCodes
from ta_core.features.event import Frequency, Weekday


class RecurrenceRule(BaseModel):
    freq: Frequency = Field(
        ...,
        title="FREQ",
        description="The FREQ rule part identifies the type of recurrence rule.",
    )

    # If the value specified by UNTIL is synchronized with the specified recurrence,
    # this DATE or DATE-TIME becomes the last instance of the recurrence.

    # The value of the UNTIL rule part MUST have the same value type as the "start" property.

    # If not present, and the COUNT rule part is also not present, the "RRULE" is considered to repeat forever.
    until: date | datetime | None = Field(
        None,
        title="UNTIL",
        description="The UNTIL rule part defines a DATE or DATE-TIME value that bounds the recurrence rule in an inclusive manner.",
    )

    count: int | None = Field(
        None,
        title="COUNT",
        description="The COUNT rule part defines the number of occurrences at which to range-bound the recurrence.",
    )

    interval: int = Field(
        1,
        title="INTERVAL",
        description="The INTERVAL rule part contains a positive integer representing at which intervals the recurrence rule repeats.",
    )

    # The BYSECOND, BYMINUTE and BYHOUR rule parts MUST NOT be specified
    # when the associated "start" property has a DATE value type.

    # If the BYSECOND, BYMINUTE, BYHOUR, BYDAY, BYMONTHDAY, or BYMONTH rule part were missing,
    # the appropriate second, minute, hour, day, or month would have been retrieved from the "start" property.
    bysecond: tuple[int, ...] | None = Field(
        None,
        title="BYSECOND",
        description="The BYSECOND rule part specifies a COMMA-separated list of seconds within a minute.",
    )

    byminute: tuple[int, ...] | None = Field(
        None,
        title="BYMINUTE",
        description="The BYMINUTE rule part specifies a COMMA-separated list of minutes within an hour.",
    )

    byhour: tuple[int, ...] | None = Field(
        None,
        title="BYHOUR",
        description="The BYHOUR rule part specifies a COMMA-separated list of hours of the day.",
    )

    # Each BYDAY value can also be preceded by a positive (+n) or negative (-n) integer.
    # If present, this indicates the nth occurrence of a specific day within the MONTHLY or YEARLY "RRULE".
    byday: tuple[tuple[int, Weekday], ...] | None = Field(
        None,
        title="BYDAY",
        description="The BYDAY rule part specifies a COMMA-separated list of days of the week.",
    )

    # The BYMONTHDAY rule part MUST NOT be specified when the FREQ rule part is set to WEEKLY.
    bymonthday: tuple[int, ...] | None = Field(
        None,
        title="BYMONTHDAY",
        description="The BYMONTHDAY rule part specifies a COMMA-separated list of days of the month.",
    )

    # The BYYEARDAY rule part MUST NOT be specified when the FREQ rule part is set to DAILY, WEEKLY, or MONTHLY.
    byyearday: tuple[int, ...] | None = Field(
        None,
        title="BYYEARDAY",
        description="The BYYEARDAY rule part specifies a COMMA-separated list of days of the year.",
    )

    # This rule part MUST NOT be used when the FREQ rule part is set to anything other than YEARLY.
    byweekno: tuple[int, ...] | None = Field(
        None,
        title="BYWEEKNO",
        description="The BYWEEKNO rule part specifies a COMMA-separated list of ordinals specifying weeks of the year.",
    )

    bymonth: tuple[int, ...] | None = Field(
        None,
        title="BYMONTH",
        description="The BYMONTH rule part specifies a COMMA-separated list of months of the year.",
    )

    # It MUST only be used in conjunction with another BYxxx rule part.
    bysetpos: tuple[int, ...] | None = Field(
        None,
        title="BYSETPOS",
        description="The BYSETPOS rule part specifies a COMMA-separated list of values that corresponds to the nth occurrence within the set of recurrence instances specified by the rule.",
    )

    wkst: Weekday = Field(
        Weekday.MO,
        title="WKST",
        description="The WKST rule part specifies the day on which the workweek starts.",
    )


class Recurrence(BaseModel):
    rrule: RecurrenceRule = Field(
        ...,
        title="RRULE",
        description="The RRULE property is the most important as it defines a regular rule for repeating the event.",
    )

    # EXDATE and RDATE can have a time zone, and must be dates (not date-times) for all-day events.
    rdate: tuple[date, ...] = Field(
        (),
        title="RDATE",
        description="The RDATE property specifies additional dates or date-times when the event occurrences should happen.",
    )

    exdate: tuple[date, ...] = Field(
        (),
        title="EXDATE",
        description="The EXDATE property is similar to RDATE, but specifies dates or date-times when the event should not happen.",
    )


class Event(BaseModel):
    summary: str = Field(..., title="Summary")
    location: str | None = Field(None, title="Location")
    start: date | datetime = Field(..., title="Start")
    end: date | datetime = Field(..., title="End")
    recurrence: Recurrence | None = Field(None, title="Recurrence")


class CreateEventRequest(BaseModel):
    event: Event = Field(..., title="Event")


class CreateEventResponse(BaseModelWithErrorCodes):
    pass
