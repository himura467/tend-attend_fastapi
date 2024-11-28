from datetime import date, datetime


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
        raise ValueError(f"Invalid time: {date_value}")
