import numpy as np, pandas as pd, datetime as dt
from datetime import datetime, timedelta, timezone

rng = pd.date_range(datetime.now(timezone.utc) - timedelta(days=1), periods=24*60, freq='min')
cr_daily_trend = pd.Series(0.025 + 0.01*np.sin(2*np.pi*(rng.hour*60 + rng.minute)/1440), index=rng)

noise = np.random.normal(0, 0.002, len(rng))

noisy_daily_trend = (cr_daily_trend + noise).clip(0.001, 0.2)

noisy_daily_trend.loc[rng[-200:-160]] -= 0.012

df = pd.DataFrame({
    "ts": rng, 
    "stream": "funnel", 
    "key": "checkout_to_purchase",
    "value": noisy_daily_trend.values,
    "tags": ["{}"]*len(rng)
})

df.to_csv("data\\synthetic_funnel.csv", index=False)
