import os, uvicorn, asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

engine = create_async_engine(os.getenv("DATABASE_URL"))

@app.get("/health")
async def health():
    return {"ok": True}

@app.get("/anomalies/latest")
async def latest():
    async with engine.connect() as conn:
        rows = (await conn.execute(text("""
                SELECT ts, stream, key, score, severity, method FROM anomalies
                ORDER BY ts DESC LIMIT 50
            """))).mappings().all()
    
    return [dict(r) for r in rows]

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
