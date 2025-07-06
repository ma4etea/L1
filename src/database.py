# import asyncio
#
# from sqlalchemy import text as text_sql
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

params = {}  # new_case: подмена engine для тестов
if settings.MODE == "test":
    params = {"poolclass": NullPool}

engine = create_async_engine(settings.DB_URL, **params)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

# new_case: позволяет повторно запускать только одно подключение к базе, нужно для asyncio.run внутри celery
engine_null_pool = create_async_engine(settings.DB_URL, poolclass=NullPool)
new_session_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)


class BaseModel(DeclarativeBase):
    pass


# async def raw(text: str):
#     async with engine.begin() as conn:
#         conn: AsyncConnection
#         result = await conn.execute(text_sql(text))
#         print(result.fetchall())
#
# asyncio.run(raw('SELECT version()'))
