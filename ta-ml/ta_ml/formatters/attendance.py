from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from ta_core.domain.entities.account import UserAccount as UserAccountEntity
from ta_core.domain.entities.event import Event as EventEntity
from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)
from ta_core.features.account import Gender
from ta_core.features.event import AttendanceAction, Frequency
from ta_core.utils.datetime import apply_timezone
from ta_core.utils.uuid import UUID, generate_uuid

from ta_ml.constants import models


def get_next_event_start(current: datetime, freq: Frequency) -> datetime:
    if freq == Frequency.SECONDLY:
        return current + timedelta(seconds=1)
    elif freq == Frequency.MINUTELY:
        return current + timedelta(minutes=1)
    elif freq == Frequency.HOURLY:
        return current + timedelta(hours=1)
    elif freq == Frequency.DAILY:
        return current + timedelta(days=1)
    elif freq == Frequency.WEEKLY:
        return current + timedelta(weeks=1)
    elif freq == Frequency.MONTHLY:
        year = current.year
        month = current.month + 1
        if month > 12:
            year += 1
            month = 1
        return current.replace(year=year, month=month)
    elif freq == Frequency.YEARLY:
        return current.replace(year=current.year + 1)
    else:
        raise ValueError(f"Unsupported frequency: {freq}")


def freq_to_stl_period(freq: Frequency) -> int:
    if freq == Frequency.SECONDLY:
        return 60
    elif freq == Frequency.MINUTELY:
        return 60
    elif freq == Frequency.HOURLY:
        return 24
    elif freq == Frequency.DAILY:
        return 7
    elif freq == Frequency.WEEKLY:
        return 4
    elif freq == Frequency.MONTHLY:
        return 12
    elif freq == Frequency.YEARLY:
        return 1
    else:
        raise ValueError(f"Unsupported frequency: {freq}")


# イベント開始時刻を -1、終了時刻を 1 として正規化
def normalize_acted_at(
    acted_at: datetime, start: datetime, duration: timedelta
) -> float:
    return ((acted_at - start).total_seconds() - duration.total_seconds() / 2) / (
        duration.total_seconds() / 2
    )


def get_formatted_attendance_data(
    earliest_attend_data: tuple[EventAttendanceActionLogEntity, ...],
    latest_leave_data: tuple[EventAttendanceActionLogEntity, ...],
    event_data: tuple[EventEntity, ...],
    user_data: tuple[UserAccountEntity, ...],
) -> tuple[pd.DataFrame, dict[tuple[int, UUID], pd.DataFrame]]:
    user_event_pairs = {
        (attend.user_id, attend.event_id) for attend in earliest_attend_data
    }
    event_dict = {}
    for event in event_data:
        event_dict[event.id] = {
            "start": event.start,
            "end": event.end,
            "duration": event.end - event.start,
            "freq": event.recurrence.rrule.freq,
            "stl_period": freq_to_stl_period(event.recurrence.rrule.freq),
        }
    user_dict = {
        user.user_id: {
            "age": (
                datetime.now(ZoneInfo("UTC")) - apply_timezone(user.birth_date, "UTC")
            ).days
            // 365,
            "gender": 0 if user.gender == Gender.MALE else 1,
        }
        for user in user_data
    }
    latest_leave_dict = {
        (leave.user_id, leave.event_id, leave.start): leave
        for leave in latest_leave_data
    }
    earliest_event_starts = {}
    for attend in earliest_attend_data:
        key = (attend.user_id, attend.event_id)
        if key not in earliest_event_starts:
            earliest_event_starts[key] = attend.start
        else:
            earliest_event_starts[key] = min(earliest_event_starts[key], attend.start)
    now = datetime.now(ZoneInfo("UTC"))
    earliest_attend_data_considering_absence = []
    for user_id, event_id in user_event_pairs:
        current = earliest_event_starts[(user_id, event_id)]
        freq = event_dict[event_id]["freq"]
        while current.replace(tzinfo=ZoneInfo("UTC")) <= now:
            existing_attend = next(
                (
                    attend
                    for attend in earliest_attend_data
                    if attend.user_id == user_id
                    and attend.event_id == event_id
                    and attend.start == current
                ),
                None,
            )
            if existing_attend:
                earliest_attend_data_considering_absence.append(existing_attend)
            else:
                earliest_attend_data_considering_absence.append(
                    EventAttendanceActionLogEntity(
                        entity_id=generate_uuid(),
                        user_id=user_id,
                        event_id=event_id,
                        start=current,
                        action=AttendanceAction.ATTEND,
                        acted_at=current
                        + event_dict[event_id][
                            "duration"
                        ],  # 欠席の場合は終了時刻を使用
                    )
                )
            current = get_next_event_start(current, freq)

    data_by_group: defaultdict[tuple[int, UUID], dict[str, list[Any]]] = defaultdict(
        lambda: {
            "user_id": [],
            "age": [],
            "gender": [],
            "event_id": [],
            "stl_period": [],
            "start": [],
            "acted_at": [],
            "duration": [],
        }
    )
    date_features_by_group = defaultdict(list)

    for attend in earliest_attend_data_considering_absence:
        key = (attend.user_id, attend.event_id)
        group_data = data_by_group[key]
        group_data["user_id"].append(attend.user_id)
        group_data["age"].append(user_dict[attend.user_id]["age"])
        group_data["gender"].append(user_dict[attend.user_id]["gender"])
        group_data["event_id"].append(attend.event_id)
        group_data["stl_period"].append(event_dict[attend.event_id]["stl_period"])
        group_data["start"].append(attend.start)
        group_data["acted_at"].append(
            normalize_acted_at(
                attend.acted_at, attend.start, event_dict[attend.event_id]["duration"]
            )
        )
        leave = latest_leave_dict.get(
            (attend.user_id, attend.event_id, attend.start),
            EventAttendanceActionLogEntity(
                entity_id=generate_uuid(),
                user_id=attend.user_id,
                event_id=attend.event_id,
                start=attend.start,
                action=AttendanceAction.LEAVE,
                acted_at=attend.start
                + event_dict[attend.event_id][
                    "duration"
                ],  # 退出ログがない場合は、イベント終了時刻に退出したものとする
            ),
        )
        # 欠席の場合は duration を 0 に設定
        if attend.acted_at >= attend.start + event_dict[attend.event_id]["duration"]:
            group_data["duration"].append(0)
        else:
            group_data["duration"].append(
                (leave.acted_at - attend.acted_at)
                / event_dict[attend.event_id]["duration"]  # 正規化
            )
        date_features_by_group[key].append(
            [
                attend.start.weekday(),
                attend.start.year,
                attend.start.month,
                attend.start.day,
            ]
        )

    filtered_groups = []
    date_features_dict = {}

    for (user_id, event_id), group_data in data_by_group.items():
        if len(group_data["acted_at"]) < models.FORECASTABLE_THRESHOLD:
            continue
        df_group = pd.DataFrame(group_data).tail(models.CONTEXT_LEN)
        filtered_groups.append(df_group)
        current_dates = np.array(date_features_by_group[(user_id, event_id)])[
            -models.CONTEXT_LEN :
        ]
        future_dates = []
        current = group_data["start"][-1]
        freq = event_dict[event_id]["freq"]
        for _ in range(models.HORIZON_LEN):
            current = get_next_event_start(current, freq)
            future_dates.append(
                [
                    current.weekday(),
                    current.year,
                    current.month,
                    current.day,
                ]
            )
        all_dates = np.vstack([current_dates, future_dates])
        date_features_dict[(user_id, event_id)] = pd.DataFrame(
            all_dates, columns=["day_of_week", "year", "month", "day"]
        )

    if not filtered_groups:
        return pd.DataFrame(), {}

    df = pd.concat(filtered_groups, axis=0, ignore_index=True)
    return df, date_features_dict


def denormalize_acted_at(
    normalized_acted_at: float, start: datetime, duration: timedelta
) -> datetime:
    """正規化された acted_at を実際の datetime に戻す

    Args:
        normalized_acted_at: 正規化された acted_at（-1 から 1 の範囲）
        start: イベント開始時刻
        duration: イベント期間

    Returns:
        実際の acted_at（datetime）
    """
    seconds_from_center = int(normalized_acted_at * (duration.total_seconds() / 2))
    center_time = start + duration / 2
    return center_time + timedelta(seconds=seconds_from_center)


def denormalize_duration(normalized_duration: float, duration: timedelta) -> float:
    """正規化された duration を実際の秒数に戻す

    Args:
        normalized_duration: 正規化された duration（0 から 1 の範囲）
        duration: イベント期間

    Returns:
        実際の duration（秒）
    """
    return normalized_duration * duration.total_seconds()
