import json

import pytest
from httpx import ASGITransport, AsyncClient
from src.config import settings
from src.database import engine_null_pool, BaseModel
from src.main import app
from src.models import *


@pytest.fixture(autouse=True, scope="session")
def check_env():
    assert settings.MODE == "test"


@pytest.fixture(autouse=True, scope="session")
async def create_table(check_env):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)




@pytest.fixture(autouse=True, scope="session")
async def register_user(create_table):
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/auth/register", json={
            "email": "str@exampel.com",
            "password": "str@exampel.com"
        })
        assert response.status_code == 200

@pytest.fixture(autouse=True, scope="session")
async def add_hotels_rooms(register_user):
    token = register_user
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        with open("tests/mock_hotels.json", "r") as file:
            hotels_: list[dict] = json.load(file)

        with open("tests/mock_rooms.json", "r") as file:
            rooms_: list[dict] = json.load(file)

        for hotel in hotels_:
            resp_hotel = await ac.post("/hotels", json=hotel)
            assert resp_hotel.status_code == 200
            hotel_id = resp_hotel.json()["data"]["id"]

            for room in rooms_:
                print(f"roommm: {room}")
                resp_room = await ac.post(f"/hotels/{hotel_id}/rooms", json=room)
                assert resp_room.status_code == 200