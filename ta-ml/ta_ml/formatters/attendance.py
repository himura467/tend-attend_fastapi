from datetime import datetime
from typing import Any

import pandas as pd
from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)

from ta_ml.constants import models


def normalize_acted_at(acted_at: datetime, start: datetime, duration: float) -> float:
    return ((acted_at - start).total_seconds() - duration / 2) / (duration / 2)


def get_formatted_attendance_data(
    raw_data: tuple[EventAttendanceActionLogEntity, ...],
    event_data: dict[str, dict[str, float]],
    user_data: dict[int, dict[str, float]],
) -> pd.DataFrame:
    data: dict[str, list[Any]] = {
        "user_id": [],
        "age": [],
        "gender": [],
        "event_id": [],
        "start": [],
        "day_of_week": [],
        "year": [],
        "month": [],
        "day": [],
        "acted_at": [],
    }
    for record in raw_data:
        data["user_id"].append(record.user_id)
        data["age"].append(user_data[record.user_id]["age"])
        data["gender"].append(user_data[record.user_id]["gender"])
        data["event_id"].append(record.event_id)
        data["start"].append(record.start)
        data["day_of_week"].append(record.start.weekday())
        data["year"].append(record.start.year)
        data["month"].append(record.start.month)
        data["day"].append(record.start.day)
        data["acted_at"].append(
            normalize_acted_at(
                record.acted_at, record.start, event_data[record.event_id]["duration"]
            )
        )

    df = pd.DataFrame(data)
    df.sort_values(by=["user_id", "event_id", "start"], inplace=True)

    return (
        df.groupby(["user_id", "event_id"])
        .filter(
            lambda group: min(
                len(group["acted_at"]) - models.HORIZON_LEN, models.CONTEXT_LEN
            )
            > models.FORECASTABLE_THRESHOLD
        )
        .groupby(["user_id", "event_id"])
        .apply(lambda group: group.tail(models.CONTEXT_LEN + models.HORIZON_LEN))
        .reset_index(drop=True)
    )
