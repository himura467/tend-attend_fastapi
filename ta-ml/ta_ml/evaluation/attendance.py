import math
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ta_core.domain.entities.event import (
    EventAttendanceActionLog as EventAttendanceActionLogEntity,
)

from ta_ml.constants.models import CONTEXT_LEN, HORIZON_LEN
from ta_ml.constants.outliers import (
    MAX_TIME_WINDOW_GAP,
    POINT_OUTLIER_SIGMOID_COEFFICIENT,
    POINT_OUTLIER_SIGMOID_THRESHOLD,
    POINT_OUTLIER_THRESHOLD,
    SUBSEQUENCE_OUTLIER_THRESHOLD,
    TIME_WINDOW_SIZE,
)
from ta_ml.formatters.attendance import get_formatted_attendance_data
from ta_ml.models.timesfm import tfm
from ta_ml.outliers.analysis import analyze_outliers
from ta_ml.outliers.detection import detect_outliers
from ta_ml.utils.auto_reg import auto_reg_predict
from ta_ml.utils.metrics import mae, mse
from ta_ml.utils.stl import stl_decompose


def sigmoid(x: float, threshold: float = 0, a: float = 1) -> float:
    return 1 / (1 + math.exp(-a * (x - threshold)))


def evaluate_metrics(
    raw_data: tuple[EventAttendanceActionLogEntity, ...],
    event_data: dict[str, dict[str, float]],
    user_data: dict[int, dict[str, float]],
) -> None:
    df = get_formatted_attendance_data(raw_data, event_data, user_data)

    actual_inputs = []
    trend_inputs = []
    seasonal_inputs = []
    residual_inputs = []
    outputs = []
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
        actual_inputs.append(group["acted_at"].values[:CONTEXT_LEN])
        # TODO: 周期はイベントの情報から取得する
        trend, seasonal, residual = stl_decompose(group["acted_at"], period=7)
        trend_inputs.append(trend.values[:CONTEXT_LEN])
        seasonal_inputs.append(seasonal.values[:CONTEXT_LEN])
        residual_inputs.append(residual.values[:CONTEXT_LEN])
        outputs.append(group["acted_at"].values[-HORIZON_LEN:])
        age.append(group["age"].iat[0])
        gender.append(group["gender"].iat[0])
        day_of_week.append(group["day_of_week"].values)
        year.append(group["year"].values)
        month.append(group["month"].values)
        day.append(group["day"].values)
        user_ids.append(user_id)
        event_ids.append(event_id)
    inputs = [t + s for t, s in zip(trend_inputs, seasonal_inputs)]

    point_outliers_df, _, mean_squared_residuals_context = detect_outliers(
        pd.DataFrame(residual_inputs), POINT_OUTLIER_THRESHOLD
    )

    mean_squared_residuals_forecast = auto_reg_predict(
        data=mean_squared_residuals_context,
        lags=32,
        start=CONTEXT_LEN,
        end=CONTEXT_LEN + HORIZON_LEN - 1,
    )

    mean_squared_residuals_sequence = pd.concat(
        [
            mean_squared_residuals_context,
            mean_squared_residuals_forecast,
        ],
        ignore_index=True,
    )

    point_outliers_df, subsequence_outliers_df = analyze_outliers(
        point_outliers_df,
        mean_squared_residuals_sequence,
        SUBSEQUENCE_OUTLIER_THRESHOLD,
        TIME_WINDOW_SIZE,
        MAX_TIME_WINDOW_GAP,
    )

    for _, po in point_outliers_df.iterrows():
        outlier_time = po["time"][0]
        outliers_ratio = po["outlier_count"] / len(residual_inputs)
        coefficient = sigmoid(
            outliers_ratio,
            POINT_OUTLIER_SIGMOID_THRESHOLD,
            POINT_OUTLIER_SIGMOID_COEFFICIENT,
        )

        for i in range(len(inputs)):
            inputs[i][outlier_time] += residual_inputs[i][outlier_time] * coefficient

    potential_event = [
        np.array(
            [
                (
                    False
                    if subsequence_outliers_df.loc[
                        (subsequence_outliers_df["time_start"] <= t)
                        & (subsequence_outliers_df["time_end"] >= t)
                    ].empty
                    else True
                )
                for t in range(CONTEXT_LEN + HORIZON_LEN)
            ]
        )
        for _ in inputs
    ]

    cov_forecast, ols_forecast = tfm.forecast_with_covariates(
        inputs=inputs,
        dynamic_numerical_covariates={
            "day_of_week": day_of_week,
            "is_weekend": [
                [1 if day >= 5 else 0 for day in day_of_week_series]
                for day_of_week_series in day_of_week
            ],
            "year": year,
            "month": month,
            "day": day,
        },
        dynamic_categorical_covariates={
            "potential_event": potential_event,
        },
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
    print(f"eval_mae_xreg_timesfm: {mae(cov_forecast, outputs)}")
    print(f"eval_mse_xreg_timesfm: {mse(cov_forecast, outputs)}")

    for i in range(len(inputs)):
        plt.figure(figsize=(12, 6))
        plt.plot(
            range(CONTEXT_LEN - len(actual_inputs[i]), CONTEXT_LEN),
            actual_inputs[i],
            label="actual_inputs",
            linestyle="--",
        )
        plt.plot(
            range(CONTEXT_LEN - len(residual_inputs[i]), CONTEXT_LEN),
            residual_inputs[i],
            label="residual_inputs",
            linestyle=":",
        )
        plt.plot(
            range(CONTEXT_LEN - len(inputs[i]), CONTEXT_LEN),
            inputs[i],
            label="inputs",
            linestyle="-",
        )
        plt.plot(
            range(CONTEXT_LEN, CONTEXT_LEN + len(outputs[i])),
            outputs[i],
            label="outputs",
            linestyle="--",
        )
        plt.plot(
            range(CONTEXT_LEN, CONTEXT_LEN + len(cov_forecast[i])),
            cov_forecast[i],
            label="forecast",
            linestyle="-",
        )
        plt.title(
            f"Time Series Forecasting for User {user_ids[i]} and Event {event_ids[i]}"
        )
        plt.xlabel("Date")
        plt.ylabel("Attended At (Normalized)")
        plt.legend(loc="upper left")
        plt.show()
