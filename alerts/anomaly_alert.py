import os, json, requests, asyncio
from sqlalchemy import create_async_engine
from sqlalchemy import text

from dotenv import load_dotenv
load_dotenv()

WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
engine = create_async_engine(os.getenv("DATABASE_URL"))

async def anomaly_alert():
    q = """SELECT * FROM anomalies WHERE ts > now() - interval '2 minutes' ORDER BY ts DESC"""

    async with engine.connect() as conn:
        rows = (await conn.execute(text(q))).mappings.all()
    
    for r in rows:
        emoji = {"critical": "🔴", "warn": "🟡", "info": "🟢"}.get(r['severity'], "ℹ️")
        message = (
            f"{emoji} *{r['severity'].upper()} ALERT*\n"
            f"• Stream: `{r['stream']}`\n"
            f"• Key: `{r['key']}`\n"
            f"• Method: `{r['method']}`\n"
            f"• Score: *{r['score']}*\n"
            f"• Time: {r['ts']}")
           
        if WEBHOOK: requests.post(WEBHOOK, json={"text": message})

if __name__ == "__main__":
    asyncio.run(anomaly_alert())