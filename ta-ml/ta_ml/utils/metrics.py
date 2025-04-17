from typing import Any

import numpy as np


def mae(
    y_pred: np.ndarray[Any, np.dtype[np.float64]] | list[float],
    y_true: np.ndarray[Any, np.dtype[np.float64]] | list[float],
) -> np.ndarray[Any, np.dtype[np.float64]]:
    y_pred = np.array(y_pred)
    y_true = np.array(y_true)
    return np.mean(np.abs(y_pred - y_true), axis=1, keepdims=True)


def mse(
    y_pred: np.ndarray[Any, np.dtype[np.float64]] | list[float],
    y_true: np.ndarray[Any, np.dtype[np.float64]] | list[float],
) -> np.ndarray[Any, np.dtype[np.float64]]:
    y_pred = np.array(y_pred)
    y_true = np.array(y_true)
    return np.mean(np.square(y_pred - y_true), axis=1, keepdims=True)
