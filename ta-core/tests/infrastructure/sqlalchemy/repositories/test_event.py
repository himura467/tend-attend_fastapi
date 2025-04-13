from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ta_core.domain.entities.event import EventAttendance as EventAttendanceEntity
from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)
from ta_core.domain.entities.event import RecurrenceRule as RecurrenceRuleEntity
from ta_core.features.event import AttendanceAction, AttendanceState, Frequency, Weekday
from ta_core.infrastructure.sqlalchemy.models.sequences.sequence import SequenceUserId
from ta_core.infrastructure.sqlalchemy.models.shards.event import (
    EventAttendanceActionLog,
)
from ta_core.infrastructure.sqlalchemy.repositories.event import (
    EventAttendanceActionLogRepository,
    EventAttendanceRepository,
    EventRepository,
    RecurrenceRepository,
    RecurrenceRuleRepository,
)
from ta_core.infrastructure.sqlalchemy.unit_of_work import SqlalchemyUnitOfWork
from ta_core.utils.uuid import UUID, generate_uuid, uuid_to_bin


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "freq, until, count, interval, bysecond, byminute, byhour, byday, bymonthday, byyearday, byweekno, bymonth, bysetpos, wkst",
    [
        (
            Frequency.DAILY,
            None,
            3,
            1,
            [0],
            [0],
            [0],
            [
                [0, Weekday.MO],
                [0, Weekday.TU],
                [0, Weekday.WE],
                [0, Weekday.TH],
                [0, Weekday.FR],
            ],
            [0],
            [0],
            [0],
            [0],
            [0],
            Weekday.MO,
        ),
    ],
)
async def test_create_recurrence_rule_async(
    test_session: AsyncSession,
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
    uow = SqlalchemyUnitOfWork(session=test_session)
    recurrence_rule_repository = RecurrenceRuleRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    recurrence_rule = await recurrence_rule_repository.create_recurrence_rule_async(
        entity_id=entity_id,
        user_id=user_id,
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

    assert recurrence_rule is not None
    assert recurrence_rule.id == entity_id
    assert recurrence_rule.user_id == user_id
    assert recurrence_rule.freq == freq
    assert recurrence_rule.until == until
    assert recurrence_rule.count == count
    assert recurrence_rule.interval == interval
    assert recurrence_rule.bysecond == bysecond
    assert recurrence_rule.byminute == byminute
    assert recurrence_rule.byhour == byhour
    assert recurrence_rule.byday == byday
    assert recurrence_rule.bymonthday == bymonthday
    assert recurrence_rule.byyearday == byyearday
    assert recurrence_rule.byweekno == byweekno
    assert recurrence_rule.bymonth == bymonth
    assert recurrence_rule.bysetpos == bysetpos
    assert recurrence_rule.wkst == wkst


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rdate, exdate",
    [
        (
            [],
            [],
        )
    ],
)
async def test_create_recurrence_async(
    test_session: AsyncSession,
    rdate: list[str],
    exdate: list[str],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    recurrence_rule_repository = RecurrenceRuleRepository(uow)
    recurrence_repository = RecurrenceRepository(uow)

    user_id = await SequenceUserId.id_generator(uow)

    recurrence_rule = await recurrence_rule_repository.create_recurrence_rule_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        freq=Frequency.DAILY,
        until=None,
        count=3,
        interval=1,
        bysecond=[0],
        byminute=[0],
        byhour=[0],
        byday=[
            [0, Weekday.MO],
            [0, Weekday.TU],
            [0, Weekday.WE],
            [0, Weekday.TH],
            [0, Weekday.FR],
        ],
        bymonthday=[0],
        byyearday=[0],
        byweekno=[0],
        bymonth=[0],
        bysetpos=[0],
        wkst=Weekday.MO,
    )

    assert recurrence_rule is not None

    entity_id = generate_uuid()

    recurrence = await recurrence_repository.create_recurrence_async(
        entity_id=entity_id,
        user_id=user_id,
        rrule_id=recurrence_rule.id,
        rrule=recurrence_rule,
        rdate=rdate,
        exdate=exdate,
    )

    assert recurrence is not None
    assert recurrence.id == entity_id
    assert recurrence.user_id == user_id
    assert recurrence.rrule_id == recurrence_rule.id
    assert recurrence.rrule == recurrence_rule
    assert recurrence.rdate == rdate
    assert recurrence.exdate == exdate

    non_persistent_recurrence_rule = RecurrenceRuleEntity(
        entity_id=generate_uuid(),
        user_id=user_id,
        freq=Frequency.DAILY,
        until=None,
        count=3,
        interval=1,
        bysecond=[0],
        byminute=[0],
        byhour=[0],
        byday=[
            [0, Weekday.MO],
            [0, Weekday.TU],
            [0, Weekday.WE],
            [0, Weekday.TH],
            [0, Weekday.FR],
        ],
        bymonthday=[0],
        byyearday=[0],
        byweekno=[0],
        bymonth=[0],
        bysetpos=[0],
        wkst=Weekday.MO,
    )

    non_persistent_recurrence = await recurrence_repository.create_recurrence_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        rrule_id=non_persistent_recurrence_rule.id,
        rrule=non_persistent_recurrence_rule,
        rdate=rdate,
        exdate=exdate,
    )

    assert non_persistent_recurrence is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "summary, location, start, end, is_all_day, timezone",
    [
        (
            "summary",
            "location",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            True,
            "UTC",
        )
    ],
)
async def test_create_event_async(
    test_session: AsyncSession,
    summary: str,
    location: str | None,
    start: datetime,
    end: datetime,
    is_all_day: bool,
    timezone: str,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    recurrence_rule_repository = RecurrenceRuleRepository(uow)
    recurrence_repository = RecurrenceRepository(uow)
    event_repository = EventRepository(uow)

    user_id = await SequenceUserId.id_generator(uow)

    recurrence_rule = await recurrence_rule_repository.create_recurrence_rule_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        freq=Frequency.DAILY,
        until=None,
        count=3,
        interval=1,
        bysecond=[0],
        byminute=[0],
        byhour=[0],
        byday=[
            [0, Weekday.MO],
            [0, Weekday.TU],
            [0, Weekday.WE],
            [0, Weekday.TH],
            [0, Weekday.FR],
        ],
        bymonthday=[0],
        byyearday=[0],
        byweekno=[0],
        bymonth=[0],
        bysetpos=[0],
        wkst=Weekday.MO,
    )

    assert recurrence_rule is not None

    recurrence = await recurrence_repository.create_recurrence_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        rrule_id=recurrence_rule.id,
        rrule=recurrence_rule,
        rdate=[],
        exdate=[],
    )

    assert recurrence is not None

    entity_id = generate_uuid()

    event = await event_repository.create_event_async(
        entity_id=entity_id,
        user_id=user_id,
        summary=summary,
        location=location,
        start=start,
        end=end,
        is_all_day=is_all_day,
        recurrence_id=recurrence.id,
        timezone=timezone,
    )

    assert event is not None
    assert event.id == entity_id
    assert event.user_id == user_id
    assert event.summary == summary
    assert event.location == location
    assert event.start == start
    assert event.end == end
    assert event.is_all_day == is_all_day
    assert event.recurrence_id == recurrence.id
    assert event.timezone == timezone
    assert event.recurrence is None

    non_existent_event = await event_repository.create_event_async(
        entity_id=generate_uuid(),
        user_id=user_id,
        summary=summary,
        location=location,
        start=start,
        end=end,
        is_all_day=is_all_day,
        recurrence_id=generate_uuid(),
        timezone=timezone,
    )

    assert non_existent_event is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "summaries, location, start, end, is_all_day, timezone",
    [
        (
            ["summary0", "summary1", "summary2"],
            "location",
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            True,
            "UTC",
        )
    ],
)
async def test_read_with_recurrence_by_user_ids_async(
    test_session: AsyncSession,
    summaries: list[str],
    location: str | None,
    start: datetime,
    end: datetime,
    is_all_day: bool,
    timezone: str,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    recurrence_rule_repository = RecurrenceRuleRepository(uow)
    recurrence_repository = RecurrenceRepository(uow)
    event_repository = EventRepository(uow)

    entity_ids = [generate_uuid() for _ in range(3)]
    user_ids = [await SequenceUserId.id_generator(uow) for _ in range(3)]

    recurrences = []
    for summary, entity_id, user_id in zip(summaries, entity_ids, user_ids):
        recurrence_rule = await recurrence_rule_repository.create_recurrence_rule_async(
            entity_id=generate_uuid(),
            user_id=user_id,
            freq=Frequency.DAILY,
            until=None,
            count=3,
            interval=1,
            bysecond=[0],
            byminute=[0],
            byhour=[0],
            byday=[
                [0, Weekday.MO],
                [0, Weekday.TU],
                [0, Weekday.WE],
                [0, Weekday.TH],
                [0, Weekday.FR],
            ],
            bymonthday=[0],
            byyearday=[0],
            byweekno=[0],
            bymonth=[0],
            bysetpos=[0],
            wkst=Weekday.MO,
        )

        assert recurrence_rule is not None

        recurrence = await recurrence_repository.create_recurrence_async(
            entity_id=generate_uuid(),
            user_id=user_id,
            rrule_id=recurrence_rule.id,
            rrule=recurrence_rule,
            rdate=[],
            exdate=[],
        )

        assert recurrence is not None
        recurrences.append(recurrence)

        event = await event_repository.create_event_async(
            entity_id=entity_id,
            user_id=user_id,
            summary=summary,
            location=location,
            start=start,
            end=end,
            is_all_day=is_all_day,
            recurrence_id=recurrence.id,
            timezone=timezone,
        )

        assert event is not None

    events = await event_repository.read_with_recurrence_by_user_ids_async(
        set(user_ids)
    )

    assert len(events) == len(user_ids)
    for event in events:
        assert event.id in entity_ids
        assert event.user_id in user_ids
        assert event.summary in summaries
        assert event.location == location
        assert event.start == start.replace(tzinfo=None)
        assert event.end == end.replace(tzinfo=None)
        assert event.is_all_day == is_all_day
        assert event.recurrence_id in [recurrence.id for recurrence in recurrences]
        assert event.timezone == timezone
        assert event.recurrence in recurrences


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "events_by_user",
    [
        {
            0: [  # ユーザー 0 のイベント
                {
                    "summary": "event 0",
                    "location": "location 0",
                    "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                    "end": datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                    "is_all_day": True,
                    "timezone": "UTC",
                    "rrule": {
                        "freq": Frequency.DAILY,
                        "count": 3,
                        "interval": 1,
                    },
                },
                {
                    "summary": "event 1",
                    "location": "location 1",
                    "start": datetime(2000, 1, 3, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                    "end": datetime(2000, 1, 4, 6, 0, 0, tzinfo=ZoneInfo("UTC")),
                    "is_all_day": False,
                    "timezone": "Asia/Tokyo",
                    "rrule": {
                        "freq": Frequency.WEEKLY,
                        "count": 4,
                        "interval": 2,
                    },
                },
            ],
            1: [  # ユーザー 1 のイベント
                {
                    "summary": "event 2",
                    "location": "location 2",
                    "start": datetime(2000, 1, 5, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                    "end": datetime(2000, 1, 6, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                    "is_all_day": True,
                    "timezone": "UTC",
                    "rrule": {
                        "freq": Frequency.MONTHLY,
                        "count": 6,
                        "interval": 1,
                    },
                },
            ],
        },
    ],
)
async def test_read_all_with_recurrence_async(
    test_session: AsyncSession,
    events_by_user: dict[int, list[dict[str, Any]]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_repository = EventRepository(uow)
    recurrence_rule_repository = RecurrenceRuleRepository(uow)
    recurrence_repository = RecurrenceRepository(uow)

    user_ids = {
        user_index: await SequenceUserId.id_generator(uow)
        for user_index in events_by_user.keys()
    }
    events_with_recurrence = []

    for user_index, events in events_by_user.items():
        user_id = user_ids[user_index]
        for event_data in events:
            recurrence_rule = (
                await recurrence_rule_repository.create_recurrence_rule_async(
                    entity_id=generate_uuid(),
                    user_id=user_id,
                    freq=event_data["rrule"]["freq"],
                    until=None,
                    count=event_data["rrule"]["count"],
                    interval=event_data["rrule"]["interval"],
                    bysecond=None,
                    byminute=None,
                    byhour=None,
                    byday=None,
                    bymonthday=None,
                    byyearday=None,
                    byweekno=None,
                    bymonth=None,
                    bysetpos=None,
                    wkst=Weekday.MO,
                )
            )
            assert recurrence_rule is not None

            recurrence = await recurrence_repository.create_recurrence_async(
                entity_id=generate_uuid(),
                user_id=user_id,
                rrule_id=recurrence_rule.id,
                rrule=recurrence_rule,
                rdate=[],
                exdate=[],
            )
            assert recurrence is not None

            event_id = generate_uuid()
            event = await event_repository.create_event_async(
                entity_id=event_id,
                user_id=user_id,
                summary=event_data["summary"],
                location=event_data["location"],
                start=event_data["start"],
                end=event_data["end"],
                is_all_day=event_data["is_all_day"],
                recurrence_id=recurrence.id,
                timezone=event_data["timezone"],
            )
            assert event is not None

            events_with_recurrence.append(
                {
                    "event": event_data,
                    "recurrence": recurrence,
                    "user_id": user_id,
                    "event_id": event_id,
                }
            )

    fetched_events = await event_repository.read_all_with_recurrence_async(where=())
    assert len(fetched_events) == sum(
        len(user_events) for user_events in events_by_user.values()
    )

    for event in fetched_events:
        matching_event = next(
            (
                e
                for e in events_with_recurrence
                if event.id == e["event_id"] and event.user_id == e["user_id"]
            ),
            None,
        )
        assert (
            matching_event is not None
        ), f"Event {event.id} not found in expected events"

        event_data = matching_event["event"]  # type: ignore[assignment]
        assert event.summary == event_data["summary"]
        assert event.location == event_data["location"]
        assert event.start == event_data["start"].replace(tzinfo=None)
        assert event.end == event_data["end"].replace(tzinfo=None)
        assert event.is_all_day == event_data["is_all_day"]
        assert event.timezone == event_data["timezone"]
        assert event.recurrence_id == matching_event["recurrence"].id  # type: ignore[attr-defined]
        assert event.recurrence == matching_event["recurrence"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_id, start, state",
    [
        (
            generate_uuid(),
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            AttendanceState.PRESENT,
        )
    ],
)
async def test_read_by_user_id_and_event_id_and_start_or_none_async(
    test_session: AsyncSession,
    event_id: UUID,
    start: datetime,
    state: AttendanceState,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_repository = EventAttendanceRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    event_attendance = EventAttendanceEntity(
        entity_id=entity_id,
        user_id=user_id,
        event_id=event_id,
        start=start,
        state=state,
    )

    await event_attendance_repository.create_async(event_attendance)
    persistent_event_attendance = await event_attendance_repository.read_by_user_id_and_event_id_and_start_or_none_async(
        user_id=user_id,
        event_id=event_id,
        start=start,
    )

    assert persistent_event_attendance is not None
    assert persistent_event_attendance.id == entity_id
    assert persistent_event_attendance.user_id == user_id
    assert persistent_event_attendance.event_id == event_id
    assert persistent_event_attendance.start == start.replace(tzinfo=None)
    assert persistent_event_attendance.state == state

    non_existent_event_attendance = await event_attendance_repository.read_by_user_id_and_event_id_and_start_or_none_async(
        user_id=user_id,
        event_id=generate_uuid(),
        start=start,
    )

    assert non_existent_event_attendance is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_id, start, state",
    [
        (
            generate_uuid(),
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            AttendanceState.PRESENT,
        )
    ],
)
async def test_create_or_update_event_attendance_async(
    test_session: AsyncSession,
    event_id: UUID,
    start: datetime,
    state: AttendanceState,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_repository = EventAttendanceRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    created_attendance = (
        await event_attendance_repository.create_or_update_event_attendance_async(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            start=start,
            state=state,
        )
    )

    assert created_attendance is not None
    assert created_attendance.id == entity_id
    assert created_attendance.user_id == user_id
    assert created_attendance.event_id == event_id
    assert created_attendance.start == start
    assert created_attendance.state == state

    updated_attendance = await event_attendance_repository.create_or_update_event_attendance_async(
        entity_id=generate_uuid(),  # 新しい ID を指定しても既存のレコードが更新される
        user_id=user_id,
        event_id=event_id,
        start=start,
        state=AttendanceState.EXCUSED_ABSENCE,
    )

    assert updated_attendance is not None
    assert updated_attendance.id == entity_id  # ID は変わらない
    assert updated_attendance.user_id == user_id
    assert updated_attendance.event_id == event_id
    assert updated_attendance.start == start.replace(tzinfo=None)
    assert (
        updated_attendance.state == AttendanceState.EXCUSED_ABSENCE
    )  # 状態が更新されている


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_id, start, action, acted_at",
    [
        (
            generate_uuid(),
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            AttendanceAction.ATTEND,
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
        )
    ],
)
async def test_create_event_attendance_action_log_async(
    test_session: AsyncSession,
    event_id: UUID,
    start: datetime,
    action: AttendanceAction,
    acted_at: datetime,
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    entity_id = generate_uuid()
    user_id = await SequenceUserId.id_generator(uow)

    created_log = await event_attendance_action_log_repository.create_event_attendance_action_log_async(
        entity_id=entity_id,
        user_id=user_id,
        event_id=event_id,
        start=start,
        action=action,
        acted_at=acted_at,
    )

    assert created_log is not None
    assert created_log.id == entity_id
    assert created_log.user_id == user_id
    assert created_log.event_id == event_id
    assert created_log.start == start
    assert created_log.action == action
    assert created_log.acted_at == acted_at


test_event_id = generate_uuid()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_attendance_action_logs",
    [
        [
            EventAttendanceActionLogEntity(
                entity_id=generate_uuid(),
                user_id=0,
                event_id=test_event_id,
                start=datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                action=AttendanceAction.ATTEND,
                acted_at=datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            ),
            EventAttendanceActionLogEntity(
                entity_id=generate_uuid(),
                user_id=0,
                event_id=test_event_id,
                start=datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                action=AttendanceAction.LEAVE,
                acted_at=datetime(2000, 1, 1, 6, 0, 0, tzinfo=ZoneInfo("UTC")),
            ),
        ],
    ],
)
async def test_bulk_create_event_attendance_action_logs_async(
    test_session: AsyncSession,
    event_attendance_action_logs: list[EventAttendanceActionLogEntity],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    await event_attendance_action_log_repository.bulk_create_event_attendance_action_logs_async(
        event_attendance_action_logs
    )
    ordered_logs = (
        await event_attendance_action_log_repository.read_order_by_limit_async(
            where=(
                EventAttendanceActionLog.user_id == 0,
                EventAttendanceActionLog.event_id == uuid_to_bin(test_event_id),
                EventAttendanceActionLog.start == datetime(2000, 1, 1, 0, 0, 0),
            ),
            order_by=EventAttendanceActionLog.acted_at.asc(),
            limit=3,
        )
    )

    assert len(ordered_logs) == 2
    assert ordered_logs[0].id == event_attendance_action_logs[0].id
    assert ordered_logs[0].user_id == 0
    assert ordered_logs[0].event_id == test_event_id
    assert ordered_logs[0].start == datetime(2000, 1, 1, 0, 0, 0)
    assert ordered_logs[0].action == AttendanceAction.ATTEND
    assert ordered_logs[0].acted_at == datetime(2000, 1, 1, 0, 0, 0)
    assert ordered_logs[1].id == event_attendance_action_logs[1].id
    assert ordered_logs[1].user_id == 0
    assert ordered_logs[1].event_id == test_event_id
    assert ordered_logs[1].start == datetime(2000, 1, 1, 0, 0, 0)
    assert ordered_logs[1].action == AttendanceAction.LEAVE
    assert ordered_logs[1].acted_at == datetime(2000, 1, 1, 6, 0, 0)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_id, start, actions, acted_ats",
    [
        (
            generate_uuid(),
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            [AttendanceAction.ATTEND, AttendanceAction.LEAVE],
            [
                datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                datetime(2000, 1, 1, 6, 0, 0, tzinfo=ZoneInfo("UTC")),
            ],
        )
    ],
)
async def test_read_by_user_id_and_event_id_and_start_async(
    test_session: AsyncSession,
    event_id: UUID,
    start: datetime,
    actions: list[AttendanceAction],
    acted_ats: list[datetime],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    entity_ids = [generate_uuid() for _ in range(len(actions))]
    user_id = await SequenceUserId.id_generator(uow)

    for action, acted_at, entity_id in zip(actions, acted_ats, entity_ids):
        created_log = await event_attendance_action_log_repository.create_event_attendance_action_log_async(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            start=start,
            action=action,
            acted_at=acted_at,
        )

        assert created_log is not None

    logs = await event_attendance_action_log_repository.read_by_user_id_and_event_id_and_start_async(
        user_id=user_id,
        event_id=event_id,
        start=start,
    )

    assert len(logs) == len(actions)
    for log in logs:
        assert log.id in entity_ids
        assert log.user_id == user_id
        assert log.event_id == event_id
        assert log.start == start.replace(tzinfo=None)
        assert log.action in actions
        assert log.acted_at in [acted_at.replace(tzinfo=None) for acted_at in acted_ats]

    non_existent_logs = await event_attendance_action_log_repository.read_by_user_id_and_event_id_and_start_async(
        user_id=user_id,
        event_id=generate_uuid(),
        start=start,
    )

    assert len(non_existent_logs) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_id, start, actions, acted_ats",
    [
        (
            generate_uuid(),
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            [AttendanceAction.ATTEND, AttendanceAction.LEAVE],
            [
                datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                datetime(2000, 1, 1, 6, 0, 0, tzinfo=ZoneInfo("UTC")),
            ],
        )
    ],
)
async def test_read_latest_by_user_id_and_event_id_and_start_or_none_async(
    test_session: AsyncSession,
    event_id: UUID,
    start: datetime,
    actions: list[AttendanceAction],
    acted_ats: list[datetime],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    entity_ids = [generate_uuid() for _ in range(len(actions))]
    user_id = await SequenceUserId.id_generator(uow)

    for action, acted_at, entity_id in zip(actions, acted_ats, entity_ids):
        created_log = await event_attendance_action_log_repository.create_event_attendance_action_log_async(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            start=start,
            action=action,
            acted_at=acted_at,
        )

        assert created_log is not None

    latest_log = await event_attendance_action_log_repository.read_latest_by_user_id_and_event_id_and_start_or_none_async(
        user_id=user_id,
        event_id=event_id,
        start=start,
    )

    assert latest_log is not None
    assert latest_log.id == entity_ids[-1]
    assert latest_log.user_id == user_id
    assert latest_log.event_id == event_id
    assert latest_log.start == start.replace(tzinfo=None)
    assert latest_log.action == actions[-1]
    assert latest_log.acted_at == acted_ats[-1].replace(tzinfo=None)

    non_existent_log = await event_attendance_action_log_repository.read_latest_by_user_id_and_event_id_and_start_or_none_async(
        user_id=user_id,
        event_id=generate_uuid(),
        start=start,
    )

    assert non_existent_log is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action_logs_by_user",
    [
        {
            0: {  # ユーザー 0
                0: [  # イベント 0
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 1, 9, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 1, 8, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),  # 最も早い attend
                    },
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 1, 7, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                ],
            },
            1: {  # ユーザー 1
                0: [  # イベント 0
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 1, 11, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),  # 最も早い attend
                    },
                ],
                1: [  # イベント 1
                    {
                        "start": datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 2, 9, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                    {
                        "start": datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 2, 8, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),  # 最も早い attend
                    },
                ],
            },
        },
    ],
)
async def test_read_all_earliest_attend_async(
    test_session: AsyncSession,
    action_logs_by_user: dict[int, dict[int, list[dict[str, Any]]]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    user_ids = {
        user_index: await SequenceUserId.id_generator(uow)
        for user_index in action_logs_by_user.keys()
    }
    event_ids = {
        event_index: generate_uuid()
        for user_dict in action_logs_by_user.values()
        for event_index in user_dict.keys()
    }

    event_attendance_action_logs = []
    expected_earliest_attends = (
        {}
    )  # 各ユーザー・イベントの組み合わせでの最も早い attend 時刻
    for user_index, event_dict in action_logs_by_user.items():
        user_id = user_ids[user_index]
        for event_index, logs in event_dict.items():
            event_id = event_ids[event_index]
            attend_logs = [
                log["acted_at"]
                for log in logs
                if log["action"] == AttendanceAction.ATTEND
            ]
            if attend_logs:
                expected_earliest_attends[(user_id, event_id)] = min(attend_logs)
            event_attendance_action_logs.extend(
                [
                    EventAttendanceActionLogEntity(
                        entity_id=generate_uuid(),
                        user_id=user_id,
                        event_id=event_id,
                        start=log["start"],
                        action=log["action"],
                        acted_at=log["acted_at"],
                    )
                    for log in logs
                ]
            )

    await event_attendance_action_log_repository.bulk_create_event_attendance_action_logs_async(
        event_attendance_action_logs
    )

    earliest_attends = (
        await event_attendance_action_log_repository.read_all_earliest_attend_async()
    )
    assert len(earliest_attends) == len(expected_earliest_attends)

    for earliest_attend in earliest_attends:
        expected_acted_at = expected_earliest_attends[
            (earliest_attend.user_id, earliest_attend.event_id)
        ]
        assert earliest_attend.acted_at == expected_acted_at.replace(tzinfo=None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action_logs_by_user",
    [
        {
            0: {  # ユーザー 0
                0: [  # イベント 0
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 1, 17, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),  # 最も遅い leave
                    },
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 1, 16, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.ATTEND,
                        "acted_at": datetime(
                            2000, 1, 1, 8, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                ],
            },
            1: {  # ユーザー 1
                0: [  # イベント 0
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 1, 19, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),  # 最も遅い leave
                    },
                    {
                        "start": datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 1, 18, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                ],
                1: [  # イベント 1
                    {
                        "start": datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 2, 17, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),  # 最も遅い leave
                    },
                    {
                        "start": datetime(2000, 1, 2, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                        "action": AttendanceAction.LEAVE,
                        "acted_at": datetime(
                            2000, 1, 2, 16, 0, 0, tzinfo=ZoneInfo("UTC")
                        ),
                    },
                ],
            },
        },
    ],
)
async def test_read_all_latest_leave_async(
    test_session: AsyncSession,
    action_logs_by_user: dict[int, dict[int, list[dict[str, Any]]]],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    user_ids = {
        user_index: await SequenceUserId.id_generator(uow)
        for user_index in action_logs_by_user.keys()
    }
    event_ids = {
        event_index: generate_uuid()
        for user_dict in action_logs_by_user.values()
        for event_index in user_dict.keys()
    }

    event_attendance_action_logs = []
    expected_latest_leaves = (
        {}
    )  # 各ユーザー・イベントの組み合わせでの最も遅い leave 時刻
    for user_index, event_dict in action_logs_by_user.items():
        user_id = user_ids[user_index]
        for event_index, logs in event_dict.items():
            event_id = event_ids[event_index]
            leave_logs = [
                log["acted_at"]
                for log in logs
                if log["action"] == AttendanceAction.LEAVE
            ]
            if leave_logs:
                expected_latest_leaves[(user_id, event_id)] = max(leave_logs)
            event_attendance_action_logs.extend(
                [
                    EventAttendanceActionLogEntity(
                        entity_id=generate_uuid(),
                        user_id=user_id,
                        event_id=event_id,
                        start=log["start"],
                        action=log["action"],
                        acted_at=log["acted_at"],
                    )
                    for log in logs
                ]
            )

    await event_attendance_action_log_repository.bulk_create_event_attendance_action_logs_async(
        event_attendance_action_logs
    )

    latest_leaves = (
        await event_attendance_action_log_repository.read_all_latest_leave_async()
    )
    assert len(latest_leaves) == len(expected_latest_leaves)

    for latest_leave in latest_leaves:
        expected_acted_at = expected_latest_leaves[
            (latest_leave.user_id, latest_leave.event_id)
        ]
        assert latest_leave.acted_at == expected_acted_at.replace(tzinfo=None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_id, start, actions, acted_ats",
    [
        (
            generate_uuid(),
            datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
            [AttendanceAction.ATTEND, AttendanceAction.LEAVE],
            [
                datetime(2000, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC")),
                datetime(2000, 1, 1, 6, 0, 0, tzinfo=ZoneInfo("UTC")),
            ],
        )
    ],
)
async def test_delete_by_user_id_and_event_id_and_start_async(
    test_session: AsyncSession,
    event_id: UUID,
    start: datetime,
    actions: list[AttendanceAction],
    acted_ats: list[datetime],
) -> None:
    uow = SqlalchemyUnitOfWork(session=test_session)
    event_attendance_action_log_repository = EventAttendanceActionLogRepository(uow)

    entity_ids = [generate_uuid() for _ in range(len(actions))]
    user_id = await SequenceUserId.id_generator(uow)

    for action, acted_at, entity_id in zip(actions, acted_ats, entity_ids):
        created_log = await event_attendance_action_log_repository.create_event_attendance_action_log_async(
            entity_id=entity_id,
            user_id=user_id,
            event_id=event_id,
            start=start,
            action=action,
            acted_at=acted_at,
        )

        assert created_log is not None

    logs_before = (
        await event_attendance_action_log_repository.read_order_by_limit_async(
            where=(
                EventAttendanceActionLog.user_id == user_id,
                EventAttendanceActionLog.event_id == uuid_to_bin(event_id),
                EventAttendanceActionLog.start == start,
            ),
            order_by=EventAttendanceActionLog.acted_at.asc(),
            limit=10,
        )
    )

    assert len(logs_before) == len(actions)

    await event_attendance_action_log_repository.delete_by_user_id_and_event_id_and_start_async(
        user_id=user_id,
        event_id=event_id,
        start=start,
    )

    logs_after = await event_attendance_action_log_repository.read_order_by_limit_async(
        where=(
            EventAttendanceActionLog.user_id == user_id,
            EventAttendanceActionLog.event_id == uuid_to_bin(event_id),
            EventAttendanceActionLog.start == start,
        ),
        order_by=EventAttendanceActionLog.acted_at.asc(),
        limit=10,
    )

    assert len(logs_after) == 0
