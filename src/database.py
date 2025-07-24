import logging
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings
from src.utils.logger_utils import exc_log_string

params = {}  # new_case: подмена engine для тестов
if settings.MODE == "test":
    params = {"poolclass": NullPool}

engine = create_async_engine(settings.DB_URL, **params)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

# new_case: позволяет повторно запускать только одно подключение к базе, нужно для asyncio.run внутри celery
engine_null_pool = create_async_engine(settings.DB_URL, poolclass=NullPool)
new_session_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)


async def check_db():
    if settings.MODE in {"local", "prod", "dev"}:
        logging.warning(f"{settings.DB_URL=}")
        try:
            async with new_session() as session:
                await session.execute(text("SELECT 1"))
                logging.info("Успешное подключение к PostgreSQL")
        except Exception as exc:
            logging.error(f"Ошибка подключения к PostgreSQL: {exc_log_string(exc)}")


class BaseModel(DeclarativeBase):
    pass


# async def raw(text: str):
#     async with engine.begin() as conn:
#         conn: AsyncConnection
#         result = await conn.execute(text_sql(text))
#         print(result.fetchall())
#
# asyncio.run(raw('SELECT version()'))
