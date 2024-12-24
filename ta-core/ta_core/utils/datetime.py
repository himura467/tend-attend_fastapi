from datetime import datetime
from zoneinfo import ZoneInfo


def apply_timezone(date_value: datetime, timezone: str) -> datetime:
    return date_value.astimezone(ZoneInfo(timezone))


def validate_date(
    is_all_day: bool, date_value: datetime | str, timezone: str | None = None
) -> None:
    try:
        if isinstance(date_value, str):
            date_value = datetime.fromisoformat(date_value)
        if timezone is not None:
            date_value = apply_timezone(date_value, timezone)
        if is_all_day:
            assert (
                date_value.hour == 0
                and date_value.minute == 0
                and date_value.second == 0
                and date_value.microsecond == 0
            )
        else:
            assert (
                date_value.minute in (0, 15, 30, 45)
                and date_value.second == 0
                and date_value.microsecond == 0
            )
    except ValueError:
        raise ValueError(f"Invalid date format: {date_value}")
    except AssertionError:
        raise ValueError(f"Invalid time: {date_value}")
