import re
from datetime import date, datetime

from ta_core.features.event import Frequency, Recurrence, RecurrenceRule, Weekday


def parse_rrule(rrule_str: str, is_all_day: bool) -> RecurrenceRule:
    rrule_str = rrule_str.replace("RRULE:", "")
    rrules = dict(pair.split("=") for pair in rrule_str.split(";"))
    freq = Frequency(rrules["FREQ"])
    until: datetime | None = None
    count = int(rrules["COUNT"]) if "COUNT" in rrules else None
    if "UNTIL" in rrules:
        if count is not None:
            raise ValueError("RRULE cannot have both COUNT and UNTIL")
        until_str = rrules["UNTIL"]
        until = (
            datetime.strptime(until_str, "%Y%m%d")
            if is_all_day
            else datetime.strptime(until_str, "%Y%m%dT%H%M%S")
        )
    interval = int(rrules["INTERVAL"]) if "INTERVAL" in rrules else 1
    bysecond = (
        tuple(map(int, rrules["BYSECOND"].split(","))) if "BYSECOND" in rrules else None
    )
    byminute = (
        tuple(map(int, rrules["BYMINUTE"].split(","))) if "BYMINUTE" in rrules else None
    )
    byhour = (
        tuple(map(int, rrules["BYHOUR"].split(","))) if "BYHOUR" in rrules else None
    )
    byday = (
        tuple(
            (
                (int(m.group(1)), Weekday(m.group(2)))
                if m.group(1)
                else (0, Weekday(m.group(2)))
            )
            for m in re.finditer(r"(-?\d+)?(\w{2})", rrules["BYDAY"])
        )
        if "BYDAY" in rrules
        else None
    )
    bymonthday = (
        tuple(map(int, rrules["BYMONTHDAY"].split(",")))
        if "BYMONTHDAY" in rrules
        else None
    )
    byyearday = (
        tuple(map(int, rrules["BYYEARDAY"].split(",")))
        if "BYYEARDAY" in rrules
        else None
    )
    byweekno = (
        tuple(map(int, rrules["BYWEEKNO"].split(","))) if "BYWEEKNO" in rrules else None
    )
    bymonth = (
        tuple(map(int, rrules["BYMONTH"].split(","))) if "BYMONTH" in rrules else None
    )
    bysetpos = (
        tuple(map(int, rrules["BYSETPOS"].split(","))) if "BYSETPOS" in rrules else None
    )
    wkst = Weekday(rrules["WKST"]) if "WKST" in rrules else Weekday.MO

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


def serialize_recurrence(recurrence: Recurrence | None, is_all_day: bool) -> list[str]:
    if not recurrence:
        return []

    rrule_str = f"RRULE:FREQ={recurrence.rrule.freq.value}"
    if recurrence.rrule.until:
        rrule_str += f";UNTIL={recurrence.rrule.until.strftime('%Y%m%d') if is_all_day else recurrence.rrule.until.strftime('%Y%m%dT%H%M%S')}"
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
        rrule_str += f";BYDAY={','.join(f'{byday[1].value}' if byday[0] == 0 else f'{byday[0]}{byday[1].value}' for byday in recurrence.rrule.byday)}"
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
        rdates = ",".join(rdate.strftime("%Y%m%d") for rdate in recurrence.rdate)
        rdate_str = f"RDATE;VALUE=DATE:{rdates}"
        recurrence_list.append(rdate_str)
    if recurrence.exdate:
        exdates = ",".join(exdate.strftime("%Y%m%d") for exdate in recurrence.exdate)
        exdate_str = f"EXDATE;VALUE=DATE:{exdates}"
        recurrence_list.append(exdate_str)

    return recurrence_list
