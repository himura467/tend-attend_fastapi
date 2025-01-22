import pandas as pd
from statsmodels.tsa.ar_model import AutoReg


def auto_reg_predict(data: pd.Series, lags: int, start: int, end: int) -> pd.Series:
    res = AutoReg(data, lags=lags).fit()
    return res.predict(start=start, end=end)
