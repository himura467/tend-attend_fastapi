from typing import Any

from statsmodels.tsa.seasonal import STL


def stl_decompose(data: Any, period: Any, **kwargs: Any) -> tuple[Any, Any, Any]:
    stl = STL(data, period=period, **kwargs)
    result = stl.fit(inner_iter=1, outer_iter=1)
    trend = result.trend
    seasonal = result.seasonal
    residual = result.resid
    return trend, seasonal, residual
