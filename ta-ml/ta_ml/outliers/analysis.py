import pandas as pd


def merge_time_windows(df: pd.DataFrame, max_gap: int) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = df.sort_values("time_start")
    merged_windows = []
    current_window = {
        "time_start": df.iloc[0]["time_start"],
        "time_end": df.iloc[0]["time_end"],
    }

    for _, row in df.iloc[1:].iterrows():
        if row["time_start"] - current_window["time_end"] <= max_gap:
            current_window["time_end"] = max(
                current_window["time_end"], row["time_end"]
            )
        else:
            merged_windows.append(current_window)
            current_window = {
                "time_start": row["time_start"],
                "time_end": row["time_end"],
            }
    merged_windows.append(current_window)

    return pd.DataFrame(merged_windows)


def analyze_outliers(
    point_outliers_df: pd.DataFrame,
    residuals_sequence: pd.Series,
    subsequence_outlier_threshold: float,
    time_window_size: int,
    max_time_window_gap: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    point_outliers = []

    if "time" in point_outliers_df.columns:
        for (time), group in point_outliers_df.groupby(["time"]):
            outlier_count = len(group)
            point_outliers.append(
                {
                    "time": time,
                    "outlier_count": outlier_count,
                }
            )

    mean_residuals_sequence = residuals_sequence.rolling(
        window=time_window_size, center=True, min_periods=1
    ).mean()

    subsequence_outliers = [
        {
            "time_start": max(0, i - time_window_size // 2),
            "time_end": min(
                len(mean_residuals_sequence) - 1, i + time_window_size // 2
            ),
            "score": mean_residuals_sequence[i],
        }
        for i in mean_residuals_sequence[
            mean_residuals_sequence > subsequence_outlier_threshold
        ].index
    ]
    subsequence_outliers_df = pd.DataFrame(subsequence_outliers)

    merged_windows_df = merge_time_windows(subsequence_outliers_df, max_time_window_gap)

    merged_subsequence_outliers = []
    for _, window in merged_windows_df.iterrows():
        window_outliers = subsequence_outliers_df[
            (subsequence_outliers_df["time_start"] >= window["time_start"])
            & (subsequence_outliers_df["time_end"] <= window["time_end"])
        ]
        mean_score = window_outliers["score"].mean()
        merged_subsequence_outliers.append(
            {
                "time_start": window["time_start"],
                "time_end": window["time_end"],
                "score": mean_score,
            }
        )

    return pd.DataFrame(point_outliers), pd.DataFrame(merged_subsequence_outliers)
