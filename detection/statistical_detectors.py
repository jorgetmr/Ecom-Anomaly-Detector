import pandas as pd, numpy as np
from statsmodels.tsa.seasonal import STL

def robust_z_scores(series, window=60):
    x = series.rolling(window, min_periods = window//2)    # min_periods avoids lots of NaNs at the start
    med = x.median
    mad = x.apply(lambda s: np.median(np.abs(s - np.median(s))), raw=False)
    z_score = 0.6745*(series - med) / (mad.replace(0, np.nan))      # making the z_score SD-comparable since we are using MAD
    return z_score


def stl_residual_z(series, period=1440, window=60):
    s = series.interpolate().fillna(method="bfill")
    residuals = STL(s, period=period, robust=True).fit().resid
    
    return (residuals - residuals.rolling(window).mean())/residuals.rolling(window).std() # standardizing residuals