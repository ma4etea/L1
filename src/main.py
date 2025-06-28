import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
# from src.database import *

from src.connectors.redis_conn import redis, Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

import uvicorn
from fastapi import FastAPI
from src.api.hotels import router as hotels_router
from src.api.auth import router as auth_router
from src.api.rooms import router as rooms_router
from src.api.booking import router as booking_router
from src.api.facilities import router as facilities_router


# from _cors_helper.load_test import router as load_test


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis.connect()
    FastAPICache.init(RedisBackend(redis.redis_client), prefix="fastapi-cache")
    yield
    await redis.close()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(rooms_router)
app.include_router(booking_router)
app.include_router(hotels_router)
app.include_router(facilities_router)
# app.include_router(load_test)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, workers=None)

# uvicorn main:app
# fastapi dev main.py
# python main.py
