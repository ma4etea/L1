from src.schemas.hotels import HotelAdd


async def test_add_hotel(db):
    hotel = HotelAdd(title="победа", location="ула столеваров")
    await db.hotels.add(hotel)
    await db.commit()
