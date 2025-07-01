from src.database import new_session
from src.schemas.hotels import HotelAdd
from src.utils.db_manager import DBManager


async def test_add_hotel():
    hotel = HotelAdd(title="победа", location="ула столеваров")
    async with DBManager(new_session) as db:
        new_mode_data = await db.hotels.add(hotel)
        print(new_mode_data)