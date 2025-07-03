from src.database import new_session, new_session_null_pool
from src.schemas.hotels import HotelAdd
from src.utils.db_manager import DBManager


async def test_add_hotel(db):
    hotel = HotelAdd(title="победа", location="ула столеваров")
    new_model_data = await db.hotels.add(hotel)
    await db.commit()
