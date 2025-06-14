# import asyncio
#
# from sqlalchemy import text as text_sql
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncConnection
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

engine = create_async_engine(settings.DB_URL)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class BaseModel(DeclarativeBase):
    pass

# async def raw(text: str):
#     async with engine.begin() as conn:
#         conn: AsyncConnection
#         result = await conn.execute(text_sql(text))
#         print(result.fetchall())
#
# asyncio.run(raw('SELECT version()'))
