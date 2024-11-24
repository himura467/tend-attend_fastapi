from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class Frequency(StrEnum):
    SECONDLY = "secondly"
    MINUTELY = "minutely"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Weekday(StrEnum):
    MO = "MO"
    TU = "TU"
    WE = "WE"
    TH = "TH"
    FR = "FR"
    SA = "SA"
    SU = "SU"


@dataclass(frozen=True)
class RecurrenceRule:
    # The FREQ rule part identifies the type of recurrence rule.
    freq: Frequency

    # RRULE can have either COUNT or UNTIL to specify the end of the event recurrence. Don't use both in the same rule.

    # The UNTIL rule part defines a DATE or DATE-TIME value that bounds the recurrence rule in an inclusive manner.

    # If the value specified by UNTIL is synchronized with the specified recurrence,
    # this DATE or DATE-TIME becomes the last instance of the recurrence.

    # The value of the UNTIL rule part MUST have the same value type as the "start" property.

    # If not present, and the COUNT rule part is also not present, the "RRULE" is considered to repeat forever.
    until: date | datetime | None

    # The COUNT rule part defines the number of occurrences at which to range-bound the recurrence.
    count: int | None

    # The INTERVAL rule part contains a positive integer representing at which intervals the recurrence rule repeats.
    interval: int

    # The BYSECOND, BYMINUTE and BYHOUR rule parts MUST NOT be specified
    # when the associated "start" property has a DATE value type.

    # If the BYSECOND, BYMINUTE, BYHOUR, BYDAY, BYMONTHDAY, or BYMONTH rule part were missing,
    # the appropriate second, minute, hour, day, or month would have been retrieved from the "start" property.

    # The BYSECOND rule part specifies a COMMA-separated list of seconds within a minute.
    bysecond: tuple[int, ...] | None

    # The BYMINUTE rule part specifies a COMMA-separated list of minutes within an hour.
    byminute: tuple[int, ...] | None

    # The BYHOUR rule part specifies a COMMA-separated list of hours of the day.
    byhour: tuple[int, ...] | None

    # The BYDAY rule part specifies a COMMA-separated list of days of the week.

    # Each BYDAY value can also be preceded by a positive (+n) or negative (-n) integer.

    # If present, this indicates the nth occurrence of a specific day within the MONTHLY or YEARLY "RRULE".
    byday: tuple[tuple[int, Weekday], ...] | None

    # The BYMONTHDAY rule part specifies a COMMA-separated list of days of the month.

    # The BYMONTHDAY rule part MUST NOT be specified when the FREQ rule part is set to WEEKLY.
    bymonthday: tuple[int, ...] | None

    # The BYYEARDAY rule part specifies a COMMA-separated list of days of the year.

    # The BYYEARDAY rule part MUST NOT be specified when the FREQ rule part is set to DAILY, WEEKLY, or MONTHLY.
    byyearday: tuple[int, ...] | None

    # The BYWEEKNO rule part specifies a COMMA-separated list of ordinals specifying weeks of the year.

    # This rule part MUST NOT be used when the FREQ rule part is set to anything other than YEARLY.
    byweekno: tuple[int, ...] | None

    # The BYMONTH rule part specifies a COMMA-separated list of months of the year.
    bymonth: tuple[int, ...] | None

    # The BYSETPOS rule part specifies a COMMA-separated list of values that corresponds to the nth occurrence within the set of recurrence instances specified by the rule.

    # It MUST only be used in conjunction with another BYxxx rule part.
    bysetpos: tuple[int, ...] | None

    # The WKST rule part specifies the day on which the workweek starts.
    wkst: Weekday


@dataclass(frozen=True)
class Recurrence:
    # The RRULE property is the most important as it defines a regular rule for repeating the event.
    rrule: RecurrenceRule

    # EXDATE and RDATE can have a time zone, and must be dates (not date-times) for all-day events.

    # The RDATE property specifies additional dates when the event occurrences should happen.
    rdate: tuple[date, ...]

    # The EXDATE property is similar to RDATE, but specifies dates when the event should not happen.
    exdate: tuple[date, ...]


@dataclass(frozen=True)
class Event:
    summary: str
    location: str | None
    start: date | datetime
    end: date | datetime
    recurrence: Recurrence | None


def validate_date(is_all_day: bool, date_value: date | datetime | str) -> None:
    try:
        parsed_datetime = (
            datetime.combine(date_value, datetime.min.time())
            if type(date_value) is date
            else (
                date_value
                if type(date_value) is datetime
                else datetime.fromisoformat(str(date_value))
            )
        )
        if is_all_day:
            assert (
                parsed_datetime.hour == 0
                and parsed_datetime.minute == 0
                and parsed_datetime.second == 0
                and parsed_datetime.microsecond == 0
            )
        else:
            assert (
                parsed_datetime.minute in (0, 15, 30, 45)
                and parsed_datetime.second == 0
                and parsed_datetime.microsecond == 0
            )
    except ValueError:
        raise ValueError(f"Invalid date format: {date_value}")
    except AssertionError:
        raise AssertionError(f"Invalid time: {date_value}")
