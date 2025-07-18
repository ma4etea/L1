from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Depends

from src.api.dependecy import DepAccess, DepDB, DepPagination, DepDateBooking
from src.exceptions.exсeptions import ObjectNotFoundException, ToBigIdException, NoAvailableRoom, InvalidDateAfterDate, \
    OffsetToBigException, LimitToBigException, BookingsNotFoundException, PageNotFoundException, \
    InvalidPaginationException, RoomNotFoundException, HotelNotFoundException
from src.api.http_exceptions.http_exeptions import RoomNotFoundHTTPException, ToBigIdHTTPException, \
    NoAvailableRoomHTTPException, \
    InvalidDateAfterDateHTTPException, OffsetToBigHTTPException, LimitToBigHTTPException, BookingsNotFoundHTTPException, \
    PageNotFoundHTTPException, InvalidPaginationHTTPException, HotelNotFoundHTTPException, RoomsNotFoundHTTPException, \
    ObjectNotFoundHTTPException
from src.schemas.base import DateBooking
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


@router.get("", description="Получить все бронирования с пагинацией")
async def get_bookings(
        db: DepDB,
        pag: DepPagination,
):
    try:
        bookings = await BookingService(db).get_bookings(page=pag.page, per_page=pag.per_page)
    except (PageNotFoundException, BookingsNotFoundException) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except OffsetToBigException:
        raise OffsetToBigHTTPException
    except LimitToBigException:
        raise LimitToBigHTTPException
    except InvalidPaginationException:
        raise InvalidPaginationHTTPException
    return {"status": "ok", "data": bookings}


@router.get("/me", description="Получить мои бронирования с пагинацией")
async def get_my_booking(user_id: DepAccess, db: DepDB, pag: DepPagination, ):
    try:
        bookings = await BookingService(db).get_my_bookings(user_id=user_id, page=pag.page, per_page=pag.per_page)
    except (PageNotFoundException, BookingsNotFoundException) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except OffsetToBigException:
        raise OffsetToBigHTTPException
    except LimitToBigException:
        raise LimitToBigHTTPException
    except InvalidPaginationException:
        raise InvalidPaginationHTTPException
    return {"status": "ok", "data": bookings}


@router.get("/available_rooms", description=(
        "Получить список свободных номеров для бронирования на указанные даты. \n"
        "- Можно указать конкретный отель с помощью параметра `hotel_id`, либо получить свободные номера по всем отелям. \n"
        "- Даты заезда (`date_from`) не раньше сегодняшнего дня. \n"
        "- Дата выезда (`date_to`) позже даты заезда. \n"
        "- Также поддерживается пагинация с параметрами `page` и `per_page`.\n\n"
        "Примеры даты:\n"
        "- `date_from` 2025-07-23\n"
        "- `date_to` 2025-07-25\n"
)

            )
async def get_available_rooms(
        date_booking: DepDateBooking,
        db: DepDB,
        pag: DepPagination,
        hotel_id: int = Query(None, description="ID отеля (опционально, чтобы фильтровать номера по отелю)"),
):
    try:
        rooms_available = await RoomService(db).get_available_rooms(
            hotel_id=hotel_id, page=pag.page, per_page=pag.per_page, date_from=date_booking.date_from, date_to=date_booking.date_to)
    except InvalidDateAfterDate:
        raise InvalidDateAfterDateHTTPException
    except (PageNotFoundException, BookingsNotFoundException, HotelNotFoundException, RoomNotFoundException) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except InvalidPaginationException:
        raise InvalidPaginationHTTPException
    except OffsetToBigException:
        raise OffsetToBigHTTPException
    except LimitToBigException:
        raise LimitToBigHTTPException

    return {"status": "ok", "data": rooms_available}


# @router.get("/my_bookings")
async def get_my_bookings(
        db: DepDB,
        pag: DepPagination,
        user_id: DepAccess,
):
    bookings = await BookingService(db).get_my_bookings_(user_id, pag)
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
