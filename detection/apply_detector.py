import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pandas as pd, numpy as np, datetime as dt, json, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from detection.statistical_detectors import robust_z_scores, stl_residual_z

from celery import shared_task

from dotenv import load_dotenv
load_dotenv()


async def detect():
    engine = create_async_engine(os.getenv("DATABASE_URL"), future=True)
    q = """
    SELECT ts, value FROM events
    WHERE stream = 'funnel' AND key='checkout_to_purchase'
        AND ts > now() - interval '90 minutes'
    ORDER BY ts
    """

    async with engine.connect() as conn:
        df = (await conn.execute(text(q))).mappings().all()
    if not df: return

    s = pd.Series([r['value'] for r in df], index = pd.to_datetime(r['ts'] for r in df))

    z_score_1 = robust_z_scores(s)
    z_score_2 = stl_residual_z(s, period=1440)

    latest_ts = s.index[-1]    #logging/alert purposes

    latest_scores = {"robust_z_scores": float(z_score_1.iloc[-1]),
                     "stl_residual_z": float(z_score_2.iloc[-1])}
    highest_z_method = max(latest_scores, key= lambda k: abs(latest_scores[k]))

    severity = "info"
    if abs(latest_scores[highest_z_method]) >= 2.5: severity = "warn"
    if abs(latest_scores[highest_z_method]) >= 3.5: severity = "critical"

    if severity != "info":
        async with engine.begin() as conn:
            await conn.execute(text("""
            INSERT INTO anomalies(ts, stream, key, score, severity, method, win, details)
            VALUES (now(), 'funnel', 'checkout_to_purchase', :latest_scores, :severity, :method, '90m', CAST(:details AS jsonb))
            """), dict(latest_scores=latest_scores[highest_z_method], severity=severity, method=highest_z_method, details=json.dumps(scores)))
        
        from alerts.anomaly_alert import anomaly_alert
        await anomaly_alert()

    await engine.dispose()
    
@shared_task(name="detection.apply_detector.celery_detect", acks_late=True, rate_limit="1/m")
def celery_detect():
    from detection.apply_detector import detect
    try:
        asyncio.run(detect())
    except Exception as e:
        print(f"Celery detection error: {e}") 


if __name__ == "__main__":
    asyncio.run(detect())
