import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi_cache.backends.inmemory import InMemoryBackend



sys.path.append(str(Path(__file__).parent.parent))
from src.database import check_db
# from src.database import *
from src.config import settings
from src.connectors.redis_conn import redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import uvicorn
from fastapi import FastAPI
from src.api.hotels import router as hotels_router
from src.api.auth import router as auth_router
from src.api.rooms import router as rooms_router
from src.api.booking import router as booking_router
from src.api.facilities import router as facilities_router
from src.api.images import router as images_router
import logging

logging.basicConfig(level=logging.INFO)

# from _cors_helper.load_test import router as load_test


@asynccontextmanager
async def lifespan(app: FastAPI):
    # new_case: способ как запускать цикличные асинхронные такси через костыль
    # asyncio.create_task(resend_email())

    await check_db()

    await redis.connect()  # new_case: создает клиент redis

    try:
        FastAPICache.init(
            RedisBackend(redis.redis_client), prefix="fastapi-cache"
        ) # new_case: это позволяет над ручками вешать декоратор @cache это redis
        logging.info("FastAPICache успешно инициализирован с Redis")
    except Exception as exc:
        logging.error(f"Ошибка инициализации FastAPICache: {type(exc).__name__}: {exc}")

    yield
    await redis.close()


# new_case: вариант использование redis в тестах если редис доступен во время теста
if settings.MODE == "test_":
    FastAPICache.init(RedisBackend(redis.redis_client), prefix="fastapi-cache")
# new_case: вместо redis использовать оперативную память, под капотом все хранится в обычном dict
if settings.MODE == "test__":
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(facilities_router)
app.include_router(images_router)
# app.include_router(load_test)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, workers=None)

# uvicorn main:app
# fastapi dev main.py
# python main.py
