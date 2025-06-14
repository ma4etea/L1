from fastapi import APIRouter, HTTPException

from src.api.dependecy import DepAccess, DepDB, DepPagination
from src.schemas.booking import BookingAdd, BookingToDB

router = APIRouter(prefix="/bookings", tags=["Бронирование"])

@router.post("")
async def add_booking(
        user_id: DepAccess,
        db: DepDB,
        data_booking: BookingAdd
):
    room = await db.rooms.get_one_none(id=data_booking.room_id)
    if not room:
        raise HTTPException(404)


    data_to_db = BookingToDB(**data_booking.model_dump(), user_id=user_id, price=room.price)
    booking = await db.bookings.add(data_to_db)
    await db.commit()
    return {"status": "ok", "data": booking}


@router.get("")
async def get_bookings(
        db: DepDB,
        pag:  DepPagination,
):
    offset = pag.per_page * pag.page - pag.per_page
    limit = pag.per_page
    bookings = await db.bookings.get_all(offset=offset, limit=limit)
    return {"status": "ok", "data": bookings}

@router.get("/me")
async def get_my_booking(
        user_id: DepAccess,
        db: DepDB
):
    bookings = await db.bookings.get_all(user_id=user_id)
    return {"status": "ok", "data": bookings}