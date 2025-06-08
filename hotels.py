from fastapi import Query, Body, Path, APIRouter

from dependecy import PaginationDep
from schemas.hotels import Hotel, HotelPatch

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
    {"id": 1, "title": "Sochi", "name": "hotel"},
    {"id": 2, "title": "Dubai", "name": "motel"},
    {"id": 3, "title": "Paris", "name": "hostel"},
    {"id": 4, "title": "Tokyo", "name": "ryokan"},
    {"id": 5, "title": "New York", "name": "apartment"},
    {"id": 6, "title": "Berlin", "name": "guesthouse"},
    {"id": 7, "title": "Rome", "name": "bnb"},
    {"id": 8, "title": "Bangkok", "name": "villa"},
    {"id": 9, "title": "Barcelona", "name": "resort"},
    {"id": 10, "title": "Cape Town", "name": "lodge"}
]


@router.get("")
def get_hotels(
        pag: PaginationDep,
        id_: int | None = Query(None, description="ID"),
        title: str | None = Query(None, description="Название отеля"),

):
    hotels_ = [
        hotel
        for hotel in hotels
        if title
           and hotel["title"].lower() == title.lower()
           and id_
           and hotel["id"] == id_
    ]
    if hotels_:
        return hotels_

    total = len(hotels)
    if 0 >= pag.per_page or pag.per_page > total:
        return {f"per_page must be from 0 to {total}"}
    total_pages = (total / pag.per_page).__ceil__()
    if not 0 < pag.page <= total_pages:
        return {"status": f"page {pag.page} does not exist"}
    start = pag.per_page * pag.page - pag.per_page
    end = pag.per_page * pag.page

    return hotels[start:end]


@router.post("")
def add_hotel(
        hotel_data: Hotel = Body(
            openapi_examples={
                "1": {
                    "summary": "Дубай",
                    "value": {"title": "Дубай мубай", "name": "sjdhisu"},
                },
                "2": {
                    "summary": "Сочи",
                    "value": {"title": "Сочи мочи", "name": "sjdhisu"},
                },
            }
        )
):
    global hotels

    hotels.append(
        {"id": len(hotels) + 1, "title": hotel_data.title, "name": hotel_data.name}
    )
    return {"status": "ok"}


@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int = Path()):
    global hotels
    if len(hotels) < 1 or hotel_id < 1:
        return {"status": "error"}
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]

    return {"status": "delete"}


@router.patch("/{hotel_id}")
def edit_hotel(hotel_id: int, hotel_data: HotelPatch):
    global hotels
    hotels_ = [hotel for hotel in hotels if hotel["id"] == hotel_id]
    hotel = hotels_[0]
    if hotel:
        if hotel_data.title:
            hotel["title"] = hotel_data.title
        if hotel_data.name:
            hotel["name"] = hotel_data.name
        return [hotel for hotel in hotels if hotel["id"] == hotel_id]
    return {"status": "error"}


@router.put(
    "/{hotel_id}",
    summary="Изменение отеля",
    description="Только полное обновление",
)
def upd_hotel(
        hotel_id: int,
        hotel_data: Hotel,
):
    global hotels
    hotels_ = [hotel for hotel in hotels if hotel["id"] == hotel_id]
    hotel = hotels_[0]
    print(hotel is hotels[hotel_id - 1])
    if hotel:
        hotel["title"] = hotel_data.title
        hotel["name"] = hotel_data.name
        return [hotel for hotel in hotels if hotel["id"] == hotel_id]
    return {"status": "error"}
