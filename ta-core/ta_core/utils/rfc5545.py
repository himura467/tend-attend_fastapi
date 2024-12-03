import re
from datetime import date, datetime

from ta_core.features.event import Frequency, Recurrence, RecurrenceRule, Weekday
from ta_core.utils.datetime import validate_date


def parse_rrule(rrule_str: str, is_all_day: bool) -> RecurrenceRule:
    rrule_str = rrule_str.replace("RRULE:", "")
    rules = dict(pair.split("=") for pair in rrule_str.split(";"))
    freq = Frequency(rules["FREQ"])
    until: date | datetime | None = None
    count = int(rules["COUNT"]) if "COUNT" in rules else None
    if "UNTIL" in rules:
        if count is not None:
            raise ValueError("RRULE cannot have both COUNT and UNTIL")
        until_str = rules["UNTIL"]
        validate_date(is_all_day, until_str)
        if is_all_day:
            until = date.fromisoformat(until_str)
        else:
            until = datetime.fromisoformat(until_str)
    interval = int(rules["INTERVAL"]) if "INTERVAL" in rules else 1
    bysecond = (
        tuple(map(int, rules["BYSECOND"].split(","))) if "BYSECOND" in rules else None
    )
    byminute = (
        tuple(map(int, rules["BYMINUTE"].split(","))) if "BYMINUTE" in rules else None
    )
    byhour = tuple(map(int, rules["BYHOUR"].split(","))) if "BYHOUR" in rules else None
    byday = (
        tuple(
            (
                (int(m.group(1)), Weekday(m.group(2)))
                if m.group(1)
                else (0, Weekday(m.group(2)))
            )
            for m in re.finditer(r"(-?\d+)?(\w{2})", rules["BYDAY"])
        )
        if "BYDAY" in rules
        else None
    )
    bymonthday = (
        tuple(map(int, rules["BYMONTHDAY"].split(",")))
        if "BYMONTHDAY" in rules
        else None
    )
    byyearday = (
        tuple(map(int, rules["BYYEARDAY"].split(","))) if "BYYEARDAY" in rules else None
    )
    byweekno = (
        tuple(map(int, rules["BYWEEKNO"].split(","))) if "BYWEEKNO" in rules else None
    )
    bymonth = (
        tuple(map(int, rules["BYMONTH"].split(","))) if "BYMONTH" in rules else None
    )
    bysetpos = (
        tuple(map(int, rules["BYSETPOS"].split(","))) if "BYSETPOS" in rules else None
    )
    wkst = Weekday(rules["WKST"]) if "WKST" in rules else Weekday.MO

    return RecurrenceRule(
        freq=freq,
        until=until,
        count=count,
        interval=interval,
        bysecond=bysecond,
        byminute=byminute,
        byhour=byhour,
        byday=byday,
        bymonthday=bymonthday,
        byyearday=byyearday,
        byweekno=byweekno,
        bymonth=bymonth,
        bysetpos=bysetpos,
        wkst=wkst,
    )


def parse_recurrence(recurrence_list: list[str], is_all_day: bool) -> Recurrence | None:
    rrule: RecurrenceRule | None = None
    rdate: list[date] = []
    exdate: list[date] = []

    if not recurrence_list:
        return None

    for rec in recurrence_list:
        if rec.startswith("RRULE:"):
            rrule = parse_rrule(rec, is_all_day)
        elif rec.startswith("RDATE;"):
            if not is_all_day:
                raise ValueError("RDATE must be date-only for all-day events")
            rdate.extend(
                datetime.strptime(date_str, "%Y%m%d").date()
                for date_str in rec.replace("RDATE;VALUE=DATE:", "").split(",")
            )
        elif rec.startswith("EXDATE;"):
            if not is_all_day:
                raise ValueError("EXDATE must be date-only for all-day events")
            exdate.extend(
                datetime.strptime(date_str, "%Y%m%d").date()
                for date_str in rec.replace("EXDATE;VALUE=DATE:", "").split(",")
            )
    if not rrule:
        raise ValueError("Missing RRULE in recurrence list")

    return Recurrence(rrule=rrule, rdate=tuple(rdate), exdate=tuple(exdate))


def serialize_recurrence(recurrence: Recurrence | None) -> list[str]:
    if not recurrence:
        return []

    rrule_str = f"RRULE:FREQ={recurrence.rrule.freq.value}"
    if recurrence.rrule.until:
        rrule_str += f";UNTIL={recurrence.rrule.until.isoformat()}"
    if recurrence.rrule.count:
        rrule_str += f";COUNT={recurrence.rrule.count}"
    rrule_str += f";INTERVAL={recurrence.rrule.interval}"
    if recurrence.rrule.bysecond:
        rrule_str += f";BYSECOND={','.join(map(str, recurrence.rrule.bysecond))}"
    if recurrence.rrule.byminute:
        rrule_str += f";BYMINUTE={','.join(map(str, recurrence.rrule.byminute))}"
    if recurrence.rrule.byhour:
        rrule_str += f";BYHOUR={','.join(map(str, recurrence.rrule.byhour))}"
    if recurrence.rrule.byday:
        rrule_str += f";BYDAY={','.join(f'{byday[0]}{byday[1].value}' for byday in recurrence.rrule.byday)}"
    if recurrence.rrule.bymonthday:
        rrule_str += f";BYMONTHDAY={','.join(map(str, recurrence.rrule.bymonthday))}"
    if recurrence.rrule.byyearday:
        rrule_str += f";BYYEARDAY={','.join(map(str, recurrence.rrule.byyearday))}"
    if recurrence.rrule.byweekno:
        rrule_str += f";BYWEEKNO={','.join(map(str, recurrence.rrule.byweekno))}"
    if recurrence.rrule.bymonth:
        rrule_str += f";BYMONTH={','.join(map(str, recurrence.rrule.bymonth))}"
    if recurrence.rrule.bysetpos:
        rrule_str += f";BYSETPOS={','.join(map(str, recurrence.rrule.bysetpos))}"
    rrule_str += f";WKST={recurrence.rrule.wkst.value}"

    recurrence_list = [rrule_str]
    if recurrence.rdate:
        rdate_str = f"RDATE;VALUE=DATE:{','.join(rdate.strftime("%Y%m%d") for rdate in recurrence.rdate)}"
        recurrence_list.append(rdate_str)
    if recurrence.exdate:
        exdate_str = f"EXDATE;VALUE=DATE:{','.join(exdate.strftime("%Y%m%d") for exdate in recurrence.exdate)}"
        recurrence_list.append(exdate_str)

    return recurrence_list
