import os, asyncio, json, pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from dotenv import load_dotenv
load_dotenv()

engine = create_async_engine(os.getenv("DATABASE_URL"))

async def replay_csv(path):
    df = pd.read_csv(path)

    async with engine.begin() as conn:
        for _, r in df.iterrows():
            await conn.execute(text("""
                INSERT INTO events(ts, stream, key, value, tags)
                VALUES (:ts, :stream, :key, :value, CAST(:tags AS jsonb))
            """), dict(ts = pd.to_datetime(r.ts), stream = r.stream, key = r.key, value = float(r.value), tags = r.tags))

            await asyncio.sleep(0)    #change to 1 to make simulate a real 1 row/sec live replay instead of instant (0)

asyncio.run(replay_csv("data\\synthetic_funnel.csv"))

