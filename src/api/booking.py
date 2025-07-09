from datetime import date

from fastapi import APIRouter, HTTPException, Query

from src.api.dependecy import DepAccess, DepDB, DepPagination
from src.exceptions.exeptions import ObjectNotFoundException, ToBigIdException, UnexpectedResultFromDbException, \
    NoAvailableRoom
from src.exceptions.utils import check_data_from_after_date_to_http_exc
from src.exceptions.http_exeptions import RoomNotFoundHTTPException, ToBigIdHTTPException, NoAvailableRoomHTTPException
from src.schemas.booking import BookingAdd, BookingToDB
from src.services.booking import BookingService
from src.services.room import RoomService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.post("")
async def add_booking(user_id: DepAccess, db: DepDB, data_booking: BookingAdd):
    try:
        booking = await BookingService(db).add_booking(user_id, data_booking)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    except NoAvailableRoom:
        raise NoAvailableRoomHTTPException
    return {"status": "ok", "data": booking}

@router.get("")
async def get_bookings(
    db: DepDB,
    pag: DepPagination,
):
    bookings = await BookingService(db).get_bookings(pag)
    return {"status": "ok", "data": bookings}




@router.get("/me")
async def get_my_booking(user_id: DepAccess, db: DepDB):
    bookings = await BookingService(db).get_my_booking(user_id)
    return {"status": "ok", "data": bookings}


@router.get("/available_rooms")
async def get_available_rooms(
    db: DepDB,
    pag: DepPagination,
    date_from: date,
    date_to: date,
    hotel_id: int = Query(None),
):
    check_data_from_after_date_to_http_exc(date_from=date_from, date_to=date_to)
    rooms_available = await RoomService(db).get_available_rooms(
        hotel_id=hotel_id, pag=pag, date_from=date_from, date_to=date_to)
    return {"status": "ok", "data": rooms_available}


@router.get("/my_bookings")
async def get_my_bookings(
    db: DepDB,
    pag: DepPagination,
    user_id: DepAccess,
):
    bookings = await BookingService(db).get_my_bookings(user_id, pag)
    return {"status": "ok", "data": bookings}


@router.get("/available_rooms_shymeyko")
async def get_available_rooms_shymeyko(
    db: DepDB,
    pag: DepPagination,
    date_from: date,
    date_to: date,
    hotel_id: int = Query(None),
):
    check_data_from_after_date_to_http_exc(date_from=date_from, date_to=date_to)
    rooms_available = await RoomService(db).get_available_rooms_shymeyko(
        hotel_id=hotel_id, pag=pag, date_from=date_from, date_to=date_to
    )
    return {"status": "ok", "data": rooms_available}
