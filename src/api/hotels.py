from datetime import date

from fastapi import Query, Body, Path, APIRouter

from src.api.dependecy import DepPagination, DepDB
from src.exceptions.exeptions import ToBigIdException, \
    HotelNotFoundException, InvalidDateAfterDate, HotelAlreadyExistsException, StmtSyntaxErrorException, \
    NotNullViolationException
from src.api.http_exceptions.http_exeptions import HotelNotFoundHTTPException, ToBigIdHTTPException, \
    InvalidDateAfterDateHTTPException, HotelAlreadyExistsHTTPException, StmtSyntaxErrorHTTPException, \
    NotNullViolationHTTPException
from src.schemas.hotels import HotelPatch, HotelAdd
from src.services.hotels import HotelService

openapi_hotel_examples = {
    "1": {
        "summary": "Дубай",
        "value": {
            "title": "Дубай мубай",
            "location": "ОАЭ, г. Дубай, Шейх Заед Роуд 15"
        },
    },
    "2": {
        "summary": "Сочи",
        "value": {
            "title": "Сочи мочи",
            "location": "Россия, г. Сочи, ул. Победы 434"
        },
    },
    "3": {
        "summary": "Париж",
        "value": {
            "title": "Париж Шанель",
            "location": "Франция, Париж, ул. Риволи 12"
        },
    },
    "4": {
        "summary": "Токио",
        "value": {
            "title": "Токийская роскошь",
            "location": "Япония, Токио, Сибуя 7-3-1"
        },
    },
    "5": {
        "summary": "Алматы",
        "value": {
            "title": "Алма Гранд",
            "location": "Казахстан, г. Алматы, пр. Абая 99"
        },
    },
}


router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_available_hotels(
        db: DepDB,
        date_from: date,
        date_to: date,
        pag: DepPagination,
        title: str | None = Query(None, description="Название отеля"),
        location: str | None = Query(None, description="Локация"),
):
    try:
        hotels = await HotelService(db).get_available_hotels(
            date_from,
            date_to,
            pag,
            title,
            location,
        )
    except InvalidDateAfterDate:
        raise InvalidDateAfterDateHTTPException

    return hotels


@router.post("")
async def add_hotel(
        db: DepDB,
        hotel_data: HotelAdd = Body(
            openapi_examples=openapi_hotel_examples
        ),
):
    try:
        hotel = await HotelService(db).add_hotel(hotel_data)
    except HotelAlreadyExistsException:
        raise HotelAlreadyExistsHTTPException
    return {"status": "ok", "data": hotel}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DepDB, hotel_id: int = Path()):
    try:
        await HotelService(db).delete_hotel(hotel_id)
        return {"status": "OK"}
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException


@router.patch("/{hotel_id}")
async def edit_hotel(db: DepDB, hotel_id: int, hotel_data: HotelPatch):
    try:
        hotel = await HotelService(db).edit_hotel(hotel_id, hotel_data, exclude_unset=True)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    except StmtSyntaxErrorException:
        raise StmtSyntaxErrorHTTPException
    except NotNullViolationException:
        raise NotNullViolationHTTPException
    return {"status": "OK", "data": hotel}


@router.put(
    "/{hotel_id}",
    summary="Изменение отеля",
    description="Только полное обновление",
)
async def upd_hotel(
        db: DepDB,
        hotel_id: int,
        hotel_data: HotelAdd,
):
    try:
        hotel = await HotelService(db).edit_hotel(hotel_id, hotel_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {"status": "OK", "data": hotel}


@router.get("/{hotel_id}")
async def get_hotel(
        db: DepDB,
        hotel_id: int = Path(ge=1),
):
    try:
        result = await HotelService(db).get_hotel(hotel_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    return result
