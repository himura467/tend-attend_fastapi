import time
from collections import defaultdict
from datetime import datetime

from ta_core.domain.entities.account import UserAccount as UserAccountEntity
from ta_core.domain.entities.event import Event as EventEntity
from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)
from ta_core.dtos.event import AttendanceTime, ForecastAttendanceTimeResponse
from ta_core.features.event import Frequency
from ta_core.utils.uuid import uuid_to_str

from ta_ml.formatters.attendance import (
    denormalize_acted_at,
    denormalize_duration,
    get_formatted_attendance_data,
    get_next_event_start,
)
from ta_ml.models.timesfm import tfm
from ta_ml.utils.stl import stl_decompose


def generate_future_event_starts(
    current: datetime, freq: Frequency, count: int
) -> list[datetime]:
    future_event_starts = []
    for _ in range(count):
        current = get_next_event_start(current, freq)
        future_event_starts.append(current)
    return future_event_starts


def forecast_attendance_time(
    earliest_attend_data: tuple[EventAttendanceActionLogEntity, ...],
    latest_leave_data: tuple[EventAttendanceActionLogEntity, ...],
    event_data: tuple[EventEntity, ...],
    user_data: tuple[UserAccountEntity, ...],
) -> ForecastAttendanceTimeResponse:
    df, date_features_dict = get_formatted_attendance_data(
        earliest_attend_data, latest_leave_data, event_data, user_data
    )

    acted_at_trend = []
    acted_at_seasonal = []
    acted_at_residual = []
    duration_trend = []
    duration_seasonal = []
    duration_residual = []
    age = []
    gender = []
    day_of_week = []
    year = []
    month = []
    day = []
    user_ids = []
    event_ids = []

    start_time = time.time()

    for (user_id, event_id), group in df.groupby(["user_id", "event_id"]):
        acted_at_t, acted_at_s, acted_at_r = stl_decompose(
            group["acted_at"], period=group["stl_period"].iat[0]
        )
        acted_at_trend.append(acted_at_t.values)
        acted_at_seasonal.append(acted_at_s.values)
        acted_at_residual.append(acted_at_r.values)
        duration_t, duration_s, duration_r = stl_decompose(
            group["duration"], period=group["stl_period"].iat[0]
        )
        duration_trend.append(duration_t.values)
        duration_seasonal.append(duration_s.values)
        duration_residual.append(duration_r.values)
        age.append(group["age"].iat[0])
        gender.append(group["gender"].iat[0])
        date_features = date_features_dict[(user_id, event_id)]
        day_of_week.append(date_features["day_of_week"].values)
        year.append(date_features["year"].values)
        month.append(date_features["month"].values)
        day.append(date_features["day"].values)
        user_ids.append(user_id)
        event_ids.append(event_id)
    acted_at_inputs = [t + s for t, s in zip(acted_at_trend, acted_at_seasonal)]
    duration_inputs = [t + s for t, s in zip(duration_trend, duration_seasonal)]

    dynamic_numerical_covariates = {
        "day_of_week": day_of_week,
        "is_weekend": [
            [1 if day >= 5 else 0 for day in day_of_week_series]
            for day_of_week_series in day_of_week
        ],
        "year": year,
        "month": month,
        "day": day,
    }

    acted_at_forecast, _ = tfm.forecast_with_covariates(
        inputs=acted_at_inputs,
        dynamic_numerical_covariates=dynamic_numerical_covariates,
        dynamic_categorical_covariates={},
        static_numerical_covariates={
            "age": age,
            "gender": gender,
        },
        static_categorical_covariates={
            "user_id": user_ids,
            "event_id": event_ids,
        },
        xreg_mode="xreg + timesfm",
        normalize_xreg_target_per_input=False,
    )

    duration_forecast, _ = tfm.forecast_with_covariates(
        inputs=duration_inputs,
        dynamic_numerical_covariates=dynamic_numerical_covariates,
        dynamic_categorical_covariates={},
        static_numerical_covariates={
            "age": age,
            "gender": gender,
        },
        static_categorical_covariates={
            "user_id": user_ids,
            "event_id": event_ids,
        },
        xreg_mode="xreg + timesfm",
        normalize_xreg_target_per_input=False,
    )

    print(f"Finished forecasting in {time.time() - start_time} seconds")

    latest_starts = {}
    for (user_id, event_id), group in df.groupby(["user_id", "event_id"]):
        latest_starts[(user_id, event_id)] = group["start"].max()

    event_dict = {
        event.id: {
            "start": event.start,
            "end": event.end,
            "duration": event.end - event.start,
            "freq": event.recurrence.rrule.freq,
        }
        for event in event_data
    }

    attendance_time_forecasts: defaultdict[
        int, defaultdict[str, list[AttendanceTime]]
    ] = defaultdict(lambda: defaultdict(list))
    for i, user_id in enumerate(user_ids):
        event_id = event_ids[i]
        latest_start = latest_starts[(user_id, event_id)]
        event_info = event_dict[event_id]
        future_starts = generate_future_event_starts(
            latest_start, event_info["freq"], len(acted_at_forecast[i])
        )
        forecasts = [
            AttendanceTime(
                start=start,
                attended_at=denormalize_acted_at(
                    acted_at_forecast[i][j],
                    start,
                    event_info["duration"],
                ),
                duration=denormalize_duration(
                    duration_forecast[i][j],
                    event_info["duration"],
                ),
            )
            for j, start in enumerate(future_starts)
        ]
        attendance_time_forecasts[user_id][uuid_to_str(event_id)].extend(forecasts)

    return ForecastAttendanceTimeResponse(
        attendance_time_forecasts=attendance_time_forecasts,
        error_codes=(),
    )
