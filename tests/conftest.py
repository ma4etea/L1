import json

import pytest
from httpx import ASGITransport, AsyncClient
from src.config import settings
from src.database import engine_null_pool, BaseModel, new_session_null_pool
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
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)



@pytest.fixture(scope="function")  # new_case: "function" это область видимости это fixture вызывается каждый раз при использовании функции
async def db(create_table):
    async with DBManager(session_factory=new_session_null_pool) as db:
        yield db


@pytest.fixture(scope="session")  # new_case: "session" вызовется один раз на всю сессию
async def ac(create_table):
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(autouse=True, scope="session")
async def register_user(create_table, ac):
    response = await ac.post("/auth/register", json={
        "email": "str@exampel.com",
        "password": "str@exampel.com"
    })
    assert response.status_code == 200


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
