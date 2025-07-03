from datetime import date

from src.schemas.booking import BookingToDB, Booking


async def test_crud_booking(db):
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
    assert isinstance(new_model_data, Booking)

    booking_get = await db.bookings.get_one_none(id=new_model_data.id)
    assert isinstance(booking_get, Booking)

    booking_edit = await db.bookings.edit(booking, id=new_model_data.id)
    assert isinstance(booking_edit, Booking)

    await db.commit()

    booking_delete = await db.bookings.delete(id=new_model_data.id)
    assert booking_delete is None

    await db.rollback()
