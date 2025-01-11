from datetime import date, datetime

import pytest

from ta_core.features.event import Frequency, Recurrence, RecurrenceRule, Weekday
from ta_core.utils.rfc5545 import parse_recurrence, parse_rrule, serialize_recurrence


@pytest.mark.parametrize(
    "rrule_str, is_all_day, expected_rrule",
    [
        (
            "FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=MO,TU,WE,TH,FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
            True,
            RecurrenceRule(
                freq=Frequency.DAILY,
                until=datetime(2000, 1, 1),
                count=None,
                interval=1,
                bysecond=(0,),
                byminute=(0,),
                byhour=(0,),
                byday=(
                    (0, Weekday.MO),
                    (0, Weekday.TU),
                    (0, Weekday.WE),
                    (0, Weekday.TH),
                    (0, Weekday.FR),
                ),
                bymonthday=(1, 2, 3, 4, 5),
                byyearday=(1, 2, 3, 4, 5),
                byweekno=(1, 2, 3, 4, 5),
                bymonth=(1, 2, 3, 4, 5),
                bysetpos=(1, 2, 3, 4, 5),
                wkst=Weekday.MO,
            ),
        ),
        (
            "FREQ=WEEKLY;UNTIL=20000101T120000;INTERVAL=1;BYSECOND=0,1,2;BYMONTHDAY=1,2,3;WKST=TU",
            False,
            RecurrenceRule(
                freq=Frequency.WEEKLY,
                until=datetime(2000, 1, 1, 12, 0, 0),
                count=None,
                interval=1,
                bysecond=(0, 1, 2),
                byminute=None,
                byhour=None,
                byday=None,
                bymonthday=(1, 2, 3),
                byyearday=None,
                byweekno=None,
                bymonth=None,
                bysetpos=None,
                wkst=Weekday.TU,
            ),
        ),
        (
            "FREQ=MONTHLY;COUNT=1;INTERVAL=1;BYDAY=1MO;WKST=WE",
            True,
            RecurrenceRule(
                freq=Frequency.MONTHLY,
                until=None,
                count=1,
                interval=1,
                bysecond=None,
                byminute=None,
                byhour=None,
                byday=((1, Weekday.MO),),
                bymonthday=None,
                byyearday=None,
                byweekno=None,
                bymonth=None,
                bysetpos=None,
                wkst=Weekday.WE,
            ),
        ),
    ],
)
def test_parse_rrule(
    rrule_str: str,
    is_all_day: bool,
    expected_rrule: RecurrenceRule,
) -> None:
    assert parse_rrule(rrule_str, is_all_day) == expected_rrule


@pytest.mark.parametrize(
    "rrule_str, is_all_day, expected_error, expected_error_message",
    [
        (
            "FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=MO,TU,WE,TH,FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO;COUNT=1",
            True,
            ValueError,
            "RRULE cannot have both COUNT and UNTIL",
        ),
        (
            "FREQ=MONTHLY;UNTIL=20000101T120000",
            True,
            ValueError,
            "unconverted data remains: T120000",
        ),
        (
            "FREQ=MONTHLY;UNTIL=20000101T001000Z",
            False,
            ValueError,
            "unconverted data remains: Z",
        ),
    ],
)
def test_parse_rrule_error(
    rrule_str: str,
    is_all_day: bool,
    expected_error: type[Exception],
    expected_error_message: str,
) -> None:
    with pytest.raises(expected_error) as error:
        parse_rrule(rrule_str, is_all_day)

    assert str(error.value) == expected_error_message


@pytest.mark.parametrize(
    "recurrence_list, is_all_day, expected_recurrence",
    [
        (
            [],
            True,
            None,
        ),
        (
            [
                "RRULE:FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=-2MO,-1TU,WE,1TH,2FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
                "RDATE;VALUE=DATE:20000102,20000103",
                "EXDATE;VALUE=DATE:19991231",
            ],
            True,
            Recurrence(
                rrule=RecurrenceRule(
                    freq=Frequency.DAILY,
                    until=datetime(2000, 1, 1),
                    count=None,
                    interval=1,
                    bysecond=(0,),
                    byminute=(0,),
                    byhour=(0,),
                    byday=(
                        (-2, Weekday.MO),
                        (-1, Weekday.TU),
                        (0, Weekday.WE),
                        (1, Weekday.TH),
                        (2, Weekday.FR),
                    ),
                    bymonthday=(1, 2, 3, 4, 5),
                    byyearday=(1, 2, 3, 4, 5),
                    byweekno=(1, 2, 3, 4, 5),
                    bymonth=(1, 2, 3, 4, 5),
                    bysetpos=(1, 2, 3, 4, 5),
                    wkst=Weekday.MO,
                ),
                rdate=(date(2000, 1, 2), date(2000, 1, 3)),
                exdate=(date(1999, 12, 31),),
            ),
        ),
        (
            [
                "RRULE:FREQ=HOURLY;UNTIL=20000101T123000;INTERVAL=1;BYSECOND=0,1,2;BYMONTHDAY=1,2,3;WKST=TU",
            ],
            False,
            Recurrence(
                rrule=RecurrenceRule(
                    freq=Frequency.HOURLY,
                    until=datetime(2000, 1, 1, 12, 30, 0),
                    count=None,
                    interval=1,
                    bysecond=(0, 1, 2),
                    byminute=None,
                    byhour=None,
                    byday=None,
                    bymonthday=(1, 2, 3),
                    byyearday=None,
                    byweekno=None,
                    bymonth=None,
                    bysetpos=None,
                    wkst=Weekday.TU,
                ),
                rdate=(),
                exdate=(),
            ),
        ),
    ],
)
def test_parse_recurrence(
    recurrence_list: list[str],
    is_all_day: bool,
    expected_recurrence: Recurrence | None,
) -> None:
    assert parse_recurrence(recurrence_list, is_all_day) == expected_recurrence


@pytest.mark.parametrize(
    "recurrence_list, is_all_day, expected_error, expected_error_message",
    [
        (
            [
                "RRULE:FREQ=DAILY;UNTIL=20000101T000000;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=-2MO,-1TU,WE,1TH,2FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
                "RDATE;VALUE=DATE:20000102,20000103",
            ],
            False,
            ValueError,
            "RDATE must be date-only for all-day events",
        ),
        (
            [
                "RRULE:FREQ=DAILY;UNTIL=20000101T000000;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=-2MO,-1TU,WE,1TH,2FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
                "EXDATE;VALUE=DATE:19991231",
            ],
            False,
            ValueError,
            "EXDATE must be date-only for all-day events",
        ),
        (
            [
                "RDATE;VALUE=DATE:20000102,20000103",
                "EXDATE;VALUE=DATE:19991231",
            ],
            True,
            ValueError,
            "Missing RRULE in recurrence list",
        ),
    ],
)
def test_parse_recurrence_error(
    recurrence_list: list[str],
    is_all_day: bool,
    expected_error: type[Exception],
    expected_error_message: str,
) -> None:
    with pytest.raises(expected_error) as error:
        parse_recurrence(recurrence_list, is_all_day)

    assert str(error.value) == expected_error_message


@pytest.mark.parametrize(
    "recurrence, is_all_day, expected_recurrence_list",
    [
        (
            None,
            True,
            [],
        ),
        (
            Recurrence(
                rrule=RecurrenceRule(
                    freq=Frequency.DAILY,
                    until=datetime(2000, 1, 1),
                    count=None,
                    interval=1,
                    bysecond=(0,),
                    byminute=(0,),
                    byhour=(0,),
                    byday=((0, Weekday.MO), (0, Weekday.TU), (0, Weekday.WE)),
                    bymonthday=(1, 2, 3),
                    byyearday=(1, 2, 3),
                    byweekno=(1, 2, 3),
                    bymonth=(1, 2, 3),
                    bysetpos=(1, 2, 3),
                    wkst=Weekday.MO,
                ),
                rdate=(date(2000, 1, 2), date(2000, 1, 3)),
                exdate=(date(1999, 12, 31),),
            ),
            True,
            [
                "RRULE:FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=MO,TU,WE;BYMONTHDAY=1,2,3;BYYEARDAY=1,2,3;BYWEEKNO=1,2,3;BYMONTH=1,2,3;BYSETPOS=1,2,3;WKST=MO",
                "RDATE;VALUE=DATE:20000102,20000103",
                "EXDATE;VALUE=DATE:19991231",
            ],
        ),
    ],
)
def test_serialize_recurrence(
    recurrence: Recurrence | None, is_all_day: bool, expected_recurrence_list: list[str]
) -> None:
    assert serialize_recurrence(recurrence, is_all_day) == expected_recurrence_list
