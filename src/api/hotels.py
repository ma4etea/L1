from datetime import date

from fastapi import Query, Body, Path, APIRouter, HTTPException

from src.api.dependecy import DepPagination, DepDB
from src.exeptions import ObjectNotFound, UnexpectedResultFromDb, ToBigId, ToBigIdHTTPException
from src.schemas.hotels import HotelPatch, HotelAdd

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
    if date_from <= date_to:
        raise HTTPException(400, "date_from должно быть больше date_to")
    per_page = pag.per_page or 3
    offset = per_page * pag.page - per_page
    limit = per_page

    return await db.hotels.get_available_hotels(
        title, location, offset, limit, date_from=date_from, date_to=date_to
    )


@router.post("")
async def add_hotel(
    db: DepDB,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Дубай",
                "value": {"title": "Дубай мубай", "location": "sjdhisu"},
            },
            "2": {
                "summary": "Сочи",
                "value": {"title": "Сочи мочи", "location": "sjdhisu"},
            },
        }
    ),
):
    hotel = await db.hotels.add(hotel_data)
    await db.commit()

    return {"status": "ok", "data": hotel}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DepDB, hotel_id: int = Path()):
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def edit_hotel(db: DepDB, hotel_id: int, hotel_data: HotelPatch):
    await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


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
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/{hotel_id}")
async def get_hotel(
    db: DepDB,
    hotel_id: int = Path(),
):
    try:
        result = await db.hotels.get_one(id=hotel_id)
    except ObjectNotFound:
        raise HTTPException(404, "Отель не найден")
    except ToBigId as exc:
        raise ToBigIdHTTPException
    if not result:
        raise HTTPException(status_code=404)
    return result
