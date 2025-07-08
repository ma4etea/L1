from datetime import date

from fastapi import APIRouter, HTTPException, Query

from src.api.dependecy import DepAccess, DepDB, DepPagination
from src.exeptions import ObjectNotFound, ToBigId, UnexpectedResultFromDb, check_data_from_after_date_to, \
    RoomNotFoundHTTPException, ToBigIdHTTPException
from src.schemas.booking import BookingAdd, BookingToDB

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.post("")
async def add_booking(user_id: DepAccess, db: DepDB, data_booking: BookingAdd):
    try:
        room = await db.rooms.get_one(id=data_booking.room_id)
    except ObjectNotFound:
        raise RoomNotFoundHTTPException
    except ToBigId as ex:
        raise ToBigIdHTTPException


    data_to_db = BookingToDB(**data_booking.model_dump(), user_id=user_id, price=room.price)
    try:
        booking = await db.bookings.add_booking(data_to_db)
    except ObjectNotFound:
        raise HTTPException(409, "Нет свободных комнат")
    except UnexpectedResultFromDb:
        raise HTTPException(400, "Ошибка! Мы уже знаем о по проблеме и исправляем её")
    await db.commit()
    return {"status": "ok", "data": booking}


@router.get("")
async def get_bookings(
    db: DepDB,
    pag: DepPagination,
):
    offset = pag.per_page * pag.page - pag.per_page
    limit = pag.per_page
    bookings = await db.bookings.get_all(offset=offset, limit=limit)
    return {"status": "ok", "data": bookings}


@router.get("/me")
async def get_my_booking(user_id: DepAccess, db: DepDB):
    bookings = await db.bookings.get_all(user_id=user_id)
    return {"status": "ok", "data": bookings}


@router.get("/available_rooms")
async def get_available_rooms(
    db: DepDB,
    pag: DepPagination,
    date_from: date,
    date_to: date,
    hotel_id: int = Query(None),
):
    check_data_from_after_date_to(date_from=date_from, date_to=date_to)

    offset = pag.per_page * pag.page - pag.per_page
    limit = pag.per_page
    rooms_available = await db.bookings.get_available_rooms(
        hotel_id=hotel_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
    )
    return {"status": "ok", "data": rooms_available}


@router.get("/my_bookings")
async def get_my_bookings(
    db: DepDB,
    pag: DepPagination,
    user_id: DepAccess,
):
    bookings = await db.bookings.get_my_bookings(user_id, pag)
    return {"status": "ok", "data": bookings}


@router.get("/available_rooms_shymeyko")
async def get_available_rooms_shymeyko(
    db: DepDB,
    pag: DepPagination,
    date_from: date,
    date_to: date,
    hotel_id: int = Query(None),
):
    check_data_from_after_date_to(date_from=date_from, date_to=date_to)
    offset = pag.per_page * pag.page - pag.per_page
    limit = pag.per_page
    rooms_available = await db.rooms.get_available_rooms_shymeyko(
        hotel_id=hotel_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
    )
    return {"status": "ok", "data": rooms_available}
