from datetime import date

from fastapi import Query, Body, Path, APIRouter

from src.api.dependecy import DepPagination, DepDB
from src.exceptions.exeptions import ToBigIdException, \
    HotelNotFoundException, InvalidDateAfterDate
from src.exceptions.http_exeptions import HotelNotFoundHTTPException, ToBigIdHTTPException, \
    InvalidDateAfterDateHTTPException
from src.schemas.hotels import HotelPatch, HotelAdd
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["Отели"])

openapi_hotel_examples = {
            "1": {
                "summary": "Дубай",
                "value": {"title": "Дубай мубай", "location": "sjdhisu"},
            },
            "2": {
                "summary": "Сочи",
                "value": {"title": "Сочи мочи", "location": "sjdhisu"},
            },
        }

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
    hotel = await HotelService(db).add_hotel(hotel_data)
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
    hotel_id: int = Path(),
):
    try:
        result = await HotelService(db).get_hotel(hotel_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    return result
