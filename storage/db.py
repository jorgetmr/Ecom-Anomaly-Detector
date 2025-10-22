
import os, json, asyncio
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, future=True)

async def init_db():
    sql = open("storage\\schema.sql").read()
    async with engine.begin() as conn:
        await conn.execute(text(sql))