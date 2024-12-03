from datetime import UTC, date, datetime

import pytest

from ta_core.features.event import Frequency, Recurrence, RecurrenceRule, Weekday
from ta_core.utils.rfc5545 import parse_recurrence, parse_rrule


@pytest.mark.parametrize(
    "rrule_str, is_all_day, expected_freq, expected_until, expected_count, expected_interval, expected_bysecond, expected_byminute, expected_byhour, expected_byday, expected_bymonthday, expected_byyearday, expected_byweekno, expected_bymonth, expected_bysetpos, expected_wkst",
    [
        (
            "FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=MO,TU,WE,TH,FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
            True,
            Frequency.DAILY,
            date(2000, 1, 1),
            None,
            1,
            (0,),
            (0,),
            (0,),
            (
                (0, Weekday.MO),
                (0, Weekday.TU),
                (0, Weekday.WE),
                (0, Weekday.TH),
                (0, Weekday.FR),
            ),
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5),
            (1, 2, 3, 4, 5),
            Weekday.MO,
        ),
        (
            "FREQ=WEEKLY;UNTIL=20000101T120000Z;INTERVAL=1;BYSECOND=0,1,2;BYMONTHDAY=1,2,3;WKST=TU",
            False,
            Frequency.WEEKLY,
            datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
            None,
            1,
            (0, 1, 2),
            None,
            None,
            None,
            (1, 2, 3),
            None,
            None,
            None,
            None,
            Weekday.TU,
        ),
        (
            "FREQ=MONTHLY;COUNT=1;INTERVAL=1;BYDAY=1MO;WKST=WE",
            True,
            Frequency.MONTHLY,
            None,
            1,
            1,
            None,
            None,
            None,
            ((1, Weekday.MO),),
            None,
            None,
            None,
            None,
            None,
            Weekday.WE,
        ),
    ],
)
def test_parse_rrule(
    rrule_str: str,
    is_all_day: bool,
    expected_freq: Frequency,
    expected_until: date | datetime | None,
    expected_count: int | None,
    expected_interval: int,
    expected_bysecond: tuple[int, ...] | None,
    expected_byminute: tuple[int, ...] | None,
    expected_byhour: tuple[int, ...] | None,
    expected_byday: tuple[tuple[int, Weekday], ...] | None,
    expected_bymonthday: tuple[int, ...] | None,
    expected_byyearday: tuple[int, ...] | None,
    expected_byweekno: tuple[int, ...] | None,
    expected_bymonth: tuple[int, ...] | None,
    expected_bysetpos: tuple[int, ...] | None,
    expected_wkst: Weekday,
) -> None:
    rrule = parse_rrule(rrule_str, is_all_day)

    assert rrule.freq == expected_freq
    assert rrule.until == expected_until
    assert rrule.count == expected_count
    assert rrule.interval == expected_interval
    assert rrule.bysecond == expected_bysecond
    assert rrule.byminute == expected_byminute
    assert rrule.byhour == expected_byhour
    assert rrule.byday == expected_byday
    assert rrule.bymonthday == expected_bymonthday
    assert rrule.byyearday == expected_byyearday
    assert rrule.byweekno == expected_byweekno
    assert rrule.bymonth == expected_bymonth
    assert rrule.bysetpos == expected_bysetpos
    assert rrule.wkst == expected_wkst


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
            "FREQ=MONTHLY;UNTIL=20000101T120000Z",
            True,
            ValueError,
            "Invalid time: 20000101T120000Z",
        ),
        (
            "FREQ=MONTHLY;UNTIL=20000101T001000Z",
            False,
            ValueError,
            "Invalid time: 20000101T001000Z",
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
                    until=date(2000, 1, 1),
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
                "RRULE:FREQ=HOURLY;UNTIL=20000101T123000Z;INTERVAL=1;BYSECOND=0,1,2;BYMONTHDAY=1,2,3;WKST=TU",
            ],
            False,
            Recurrence(
                rrule=RecurrenceRule(
                    freq=Frequency.HOURLY,
                    until=datetime(2000, 1, 1, 12, 30, 0, tzinfo=UTC),
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
    recurrence = parse_recurrence(recurrence_list, is_all_day)

    assert recurrence == expected_recurrence


@pytest.mark.parametrize(
    "recurrence_list, is_all_day, expected_error, expected_error_message",
    [
        (
            [
                "RRULE:FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=-2MO,-1TU,WE,1TH,2FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
                "RDATE;VALUE=DATE:20000102,20000103",
            ],
            False,
            ValueError,
            "RDATE must be date-only for all-day events",
        ),
        (
            [
                "RRULE:FREQ=DAILY;UNTIL=20000101;INTERVAL=1;BYSECOND=0;BYMINUTE=0;BYHOUR=0;BYDAY=-2MO,-1TU,WE,1TH,2FR;BYMONTHDAY=1,2,3,4,5;BYYEARDAY=1,2,3,4,5;BYWEEKNO=1,2,3,4,5;BYMONTH=1,2,3,4,5;BYSETPOS=1,2,3,4,5;WKST=MO",
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
