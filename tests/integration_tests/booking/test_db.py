from datetime import date

from src.schemas.booking import BookingToDB


async def test_add_booking(db):
    users = await db.auth.get_all()
    rooms = await db.rooms.get_all()

    booking = BookingToDB(
        date_from=date(year=2025, month=7, day=5),
        date_to=date(year=2025, month=7, day=3),
        user_id=users[0].id,
        room_id=rooms[0].id,
        price=1500
    )
    new_model_data = await db.bookings.add(booking)
    await db.commit()
