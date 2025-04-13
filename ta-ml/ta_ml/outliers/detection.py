import numpy as np
import pandas as pd


def detect_outliers(
    residuals_df: pd.DataFrame,
    point_outlier_threshold: float,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    point_outliers: list[dict[str, int | float]] = []
    residuals = []
    squared_residuals = []

    for i, residual in residuals_df.iterrows():
        squared_residual = residual.pow(2)
        point_outliers_indices = squared_residual[
            squared_residual > point_outlier_threshold
        ].index
        point_outliers.extend(
            {
                "residual_index": i,
                "time": t,
                "score": squared_residual[t],
            }
            for t in point_outliers_indices
        )
        residuals.append(residual)
        squared_residuals.append(squared_residual)

    point_outliers_df = pd.DataFrame(point_outliers)
    mean_residuals = pd.Series(np.mean(residuals, axis=0))
    mean_squared_residuals = pd.Series(np.mean(squared_residuals, axis=0))

    return point_outliers_df, mean_residuals, mean_squared_residuals
