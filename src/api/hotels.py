from fastapi import Query, Body, Path, APIRouter
from sqlalchemy import Insert, literal, select, Select, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.api.dependecy import PaginationDep
from src.database import new_session, engine
from src.models.hotels import HotelsOrm
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPatch

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("")
async def get_hotels(
        pag: PaginationDep,
        title: str | None = Query(None, description="Название отеля"),
        location: str | None = Query(None, description="Локация"),

):
    per_page = pag.per_page or 3
    offset = per_page * pag.page - per_page
    limit = per_page

    async with new_session() as session:
        return await HotelsRepository(session).get_all(title, location, offset, limit)



    # async with new_session() as session:
    #     session: AsyncSession
    #     result = await session.execute(query)
    #     return result.scalars().all()


@router.post("")
async def add_hotel(
        hotel_data: Hotel = Body(
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
        )
):
    async with new_session() as session:
        session: AsyncSession
        add_hotel_stmt = Insert(HotelsOrm).values(**hotel_data.model_dump())
        print(add_hotel_stmt.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_hotel_stmt)
        await session.commit()

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
