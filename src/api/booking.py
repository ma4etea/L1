from datetime import date

from fastapi import APIRouter, Query

from src.api.dependecy import DepAccess, DepDB, DepPagination
from src.exceptions.exeptions import ObjectNotFoundException, ToBigIdException, NoAvailableRoom, InvalidDateAfterDate, \
    OffsetToBigException, LimitToBigException
from src.api.http_exceptions.http_exeptions import RoomNotFoundHTTPException, ToBigIdHTTPException, \
    NoAvailableRoomHTTPException, \
    InvalidDateAfterDateHTTPException, OffsetToBigHTTPException, LimitToBigHTTPException
from src.schemas.booking import BookingAdd
from src.services.booking import BookingService
from src.services.room import RoomService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.post("", description=(
        "Создание бронирования комнаты.\n\n"
        "Параметры:\n"
        "- `date_from` — дата заезда (check-in), должна быть сегодня или позже.\n"
        "- `date_to` — дата выезда (check-out), должна быть строго больше `date_from`.\n"
        "- `room_id` — идентификатор комнаты, должен быть положительным целым числом.\n\n"
        "Пример:\n"
        "- date_from: `2026-07-17`\n"
        "- date_to: `2026-07-25`\n"
        "- room_id: `123`\n\n"
        "Важно: бронирование предполагает проживание с даты заезда включительно и освобождение номера в день выезда.\n"
        "Даты указаны в формате ГГГГ-ММ-ДД.\n"
        "Нарушение этих условий приведёт к ошибке валидации с кодом 422."
)
             )
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
    try:
        bookings = await BookingService(db).get_bookings(pag)
    except OffsetToBigException:
        raise OffsetToBigHTTPException
    except LimitToBigException:
        raise LimitToBigHTTPException
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
    try:
        rooms_available = await RoomService(db).get_available_rooms(
            hotel_id=hotel_id, pag=pag, date_from=date_from, date_to=date_to)
    except InvalidDateAfterDate:
        raise InvalidDateAfterDateHTTPException
    return {"status": "ok", "data": rooms_available}


@router.get("/my_bookings")
async def get_my_bookings(
        db: DepDB,
        pag: DepPagination,
        user_id: DepAccess,
):
    bookings = await BookingService(db).get_my_bookings(user_id, pag)
    return {"status": "ok", "data": bookings}


# @router.get("/available_rooms_shymeyko")
async def get_available_rooms_shymeyko(
        db: DepDB,
        pag: DepPagination,
        date_from: date,
        date_to: date,
        hotel_id: int = Query(None),
):
    try:
        rooms_available = await RoomService(db).get_available_rooms_shymeyko(
            hotel_id=hotel_id, pag=pag, date_from=date_from, date_to=date_to
        )
    except InvalidDateAfterDate:
        raise InvalidDateAfterDateHTTPException
    return {"status": "ok", "data": rooms_available}
