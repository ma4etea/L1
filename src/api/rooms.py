from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Path, Body
from src.api.dependecy import DepAccess, DepDB
from src.exceptions.exeptions import ObjectNotFoundException, ToBigIdException, RoomNotFoundException, \
    HotelNotFoundException
from src.api.http_exceptions.http_exeptions import HotelNotFoundHTTPException, RoomNotFoundHTTPException, \
    ToBigIdHTTPException, \
    FacilityNotFoundHTTPException, RoomsNotFoundHTTPException
from src.schemas.facilities import AddRoomsFacilities
from src.schemas.rooms import AddRoom, AddRoomToDb, EditRoom
from src.services.room import RoomService

openapi_room_examples = {
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

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(_: DepAccess, db: DepDB, hotel_id: Annotated[int, Path(ge=1)]):
    try:
        rooms_with = await RoomService(db).get_rooms(hotel_id=hotel_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomsNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {
        "status": "OK",
        "data": rooms_with,
    }


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    _: DepAccess,
    db: DepDB,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    try:
        room = await RoomService(db).get_room(hotel_id, room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {"status": "OK", "data": room}


@router.post("/{hotel_id}/rooms")
async def create_room(
        db: DepDB,
        room_data: AddRoom = Body(openapi_examples=openapi_room_examples), # todo сделать примеры для добавления номера. и вернуть удобства
        hotel_id: int = Path()):
    new_room_data = AddRoomToDb(**room_data.model_dump(), hotel_id=hotel_id)
    try:
        room = await db.rooms.add(new_room_data)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException

    try:
        await db.rooms_facilities.add_bulk(
            [AddRoomsFacilities(room_id=room.id, facility_id=id_) for id_ in room_data.facilities_ids]
        )
    except ObjectNotFoundException:
        raise FacilityNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException

    await db.commit()

    return {
        "status": "OK",
        "data": room,
    }


@router.delete("/{hotel_id}/rooms/{room_id}")
async def remove_room(
    _: DepAccess,
    db: DepDB,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    try:
        await RoomService(db).remove_room(hotel_id, room_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {"status": "OK"}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
    db: DepDB,
    _: DepAccess,
    room_data: AddRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    start_data = datetime.now()
    try:
        room = await db.rooms.edit_room(room_data, hotel_id=hotel_id, room_id=room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException
    except ToBigIdException:
        raise ToBigIdHTTPException

    end_data = datetime.now()
    print(end_data - start_data)

    return {"status": "OK", "data": room}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def edit_room(
    _: DepAccess,
    db: DepDB,
    room_data: EditRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    room = await db.rooms.edit_room(
        room_data, exclude_unset=True, hotel_id=hotel_id, room_id=room_id
    )
    await db.commit()

    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms_shymeiko/{room_id}")
async def update_room_shymeiko(
    db: DepDB,
    _: DepAccess,
    room_data: AddRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    start_data = datetime.now()
    if room_data.facilities_ids is not None:
        await db.rooms_facilities.set_facilities_to_room(room_id, room_data.facilities_ids)

    new_room_data = EditRoom(**room_data.model_dump(exclude={"facilities_ids"}))

    room = await db.rooms.edit(new_room_data, id=room_id, exclude_unset=True)
    await db.commit()
    end_data = datetime.now()
    print(end_data - start_data)
    return {"status": "OK", "data": room}


@router.patch("/{hotel_id}/rooms_shymeiko/{room_id}")
async def edit_room_shymeiko(
    _: DepAccess,
    db: DepDB,
    room_data: EditRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    start_data = datetime.now()
    if room_data.facilities_ids is not None:
        await db.rooms_facilities.set_facilities_to_room(room_id, room_data.facilities_ids)

    new_room_data_dict = room_data.model_dump(exclude={"facilities_ids"}, exclude_unset=True)

    if new_room_data_dict:
        new_room_data = EditRoom(**new_room_data_dict)
        room = await db.rooms.edit(new_room_data, id=room_id, exclude_unset=True)
    else:
        room = await db.rooms.get_one_none(id=room_id)
    await db.commit()
    end_data = datetime.now()
    print(end_data - start_data)
    return {"status": "OK", "data": room}
