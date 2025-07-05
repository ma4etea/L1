import json

import pytest
from unittest import mock

# new_case: Декоратор заглушка для redis
# new_case: 🔹 Сначала принимает аргументы для декоратора,
# new_case: 🔹 Затем возвращает пустой декоратор,
# new_case: 🔹 Который принимает функцию и возвращает её без изменений.
# new_case: 💡 Это шаблон "заглушки" для любых декораторов с параметрами.
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda func: func).start()

from httpx import ASGITransport, AsyncClient
from src.config import settings
from src.database import BaseModel, new_session_null_pool, engine, new_session
from src.main import app
from src.models import *
from src.schemas.hotels import Hotel, HotelAdd
from src.schemas.room import AddRoomToDb
from src.utils.db_manager import DBManager


@pytest.fixture(autouse=True, scope="session")
def check_env():
    assert settings.MODE == "test"


@pytest.fixture(autouse=True, scope="session")
async def create_table(check_env):
    async with engine.begin() as conn:  # new_case: Важно что engine должен быть с параметром poolclass=NullPool
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)


@pytest.fixture(
    scope="function")  # new_case: "function" это область видимости это fixture вызывается каждый раз при использовании функции
async def db(create_table):
    async with DBManager(session_factory=new_session) as db:
        yield db


@pytest.fixture(scope="session")  # new_case: "session" вызовется один раз на всю сессию
async def ac(create_table):
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True, scope="session")
async def register_user(create_table, ac):
    creds = {
        "email": "str@exampel.com",
        "password": "str@exampel.com"
    }
    response = await ac.post("/auth/register", json=creds)
    assert response.status_code == 200
    return creds


# new_case: заполнение тестовыми данными, нужно использовать один раз свой db_ внутри
@pytest.fixture(autouse=True, scope="session")
async def add_hotels_rooms(create_table):
    with open("tests/mock_hotels.json", "r") as file:
        hotels_: list[dict] = json.load(file)

    with open("tests/mock_rooms.json", "r") as file:
        rooms_: list[dict] = json.load(file)

    hotel_models = [HotelAdd.model_validate(model) for model in hotels_]
    rooms_models = [AddRoomToDb.model_validate(model) for model in rooms_]

    async with DBManager(session_factory=new_session_null_pool) as db_:
        await db_.hotels.add_bulk(hotel_models)
        await db_.rooms.add_bulk(rooms_models)
        await db_.commit()


@pytest.fixture(scope="session")
async def auth_ac(register_user, ac):
    creds = register_user
    response = await ac.post("/auth/login", json=creds)
    assert response.status_code == 200
    print(f'{ac.cookies =}')
    assert ac.cookies["access_token"]
    yield ac
