from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Path, Body
from src.api.dependecy import DepAccess, DepDB
from src.exceptions.exсeptions import (
    ToBigIdException,
    RoomNotFoundException,
    HotelNotFoundException,
    FacilityNotFoundException,
    FacilityToBigIdException,
    RoomHaveBookingException,
    RoomMissingToHotelException,
)
from src.api.http_exceptions.http_exeptions import (
    ToBigIdHTTPException,
    ObjectNotFoundHTTPException,
    ObjectHaveForeignKeyHTTPException,
)
from src.schemas.rooms import AddRoom, EditRoom
from src.services.room import RoomService

openapi_room_examples = {
    "1": {
        "summary": "Студия",
        "value": {
            "title": "Студия",
            "description": "С видом на бархан",
            "price": 1300,
            "quantity": 5,
            "facilities_ids": [1],
        },
    },
    "2": {
        "summary": "Стандартный",
        "value": {
            "title": "Стандартный номер",
            "description": "Уютный номер с двуспальной кроватью",
            "price": 2200,
            "quantity": 8,
            "facilities_ids": [1, 2],
        },
    },
    "3": {
        "summary": "Семейный",
        "value": {
            "title": "Семейный номер",
            "description": "Просторный номер с двумя спальнями",
            "price": 3500,
            "quantity": 3,
            "facilities_ids": [1, 2, 4],
        },
    },
    "4": {
        "summary": "Люкс",
        "value": {
            "title": "Люкс",
            "description": "Роскошный номер с джакузи и балконом",
            "price": 4800,
            "quantity": 2,
            "facilities_ids": [1, 2, 3, 4],
        },
    },
    "5": {
        "summary": "Апартаменты",
        "value": {
            "title": "Апартаменты",
            "description": "С видом на море",
            "price": 5500,
            "quantity": 1,
            "facilities_ids": [1, 2, 3, 4, 5],
        },
    },
}

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(_: DepAccess, db: DepDB, hotel_id: Annotated[int, Path(ge=1)]):
    try:
        rooms_with = await RoomService(db).get_rooms(hotel_id=hotel_id)
    except (RoomNotFoundException, HotelNotFoundException) as exc:
        raise ObjectNotFoundHTTPException(exc)
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
    hotel_id: int = Path(ge=1),
    room_id: int = Path(ge=1),
):
    try:
        room = await RoomService(db).get_room(hotel_id, room_id)
    except (RoomNotFoundException, HotelNotFoundException) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {"status": "OK", "data": room}


@router.post("/{hotel_id}/rooms")
async def create_room(
    db: DepDB,
    room_data: AddRoom = Body(openapi_examples=openapi_room_examples),
    hotel_id: int = Path(ge=1),
):
    try:
        room_with = await RoomService(db).create_room(hotel_id, room_data)
    except (FacilityNotFoundException, HotelNotFoundException) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except (FacilityToBigIdException, ToBigIdException) as exc:
        raise ToBigIdHTTPException(detail=exc.details)

    return {
        "status": "OK",
        "data": room_with,
    }


@router.delete("/{hotel_id}/rooms/{room_id}")
async def remove_room(
    _: DepAccess,
    db: DepDB,
    hotel_id: int = Path(ge=1),
    room_id: int = Path(ge=1),
):
    try:
        await RoomService(db).remove_room(hotel_id, room_id)
    except (RoomNotFoundException, HotelNotFoundException, RoomMissingToHotelException) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except RoomHaveBookingException as exc:
        raise ObjectHaveForeignKeyHTTPException(exc)
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {"status": "OK"}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
    db: DepDB,
    _: DepAccess,
    room_data: AddRoom = Body(openapi_examples=openapi_room_examples),
    hotel_id: int = Path(ge=1),
    room_id: int = Path(ge=1),
):
    try:
        room_with = await RoomService(db).update_room(room_data, hotel_id=hotel_id, room_id=room_id)
    except (
        RoomNotFoundException,
        HotelNotFoundException,
        FacilityNotFoundException,
        RoomMissingToHotelException,
    ) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except ToBigIdException:
        raise ToBigIdHTTPException

    return {"status": "OK", "data": room_with}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    description=(
        "- Изменяет параметры комнаты в указанном отеле.\n"
        "- Обновление происходит частично: можно передать одно или несколько полей.\n"
        "- Если не передано ни одного поля — вернётся ошибка 422.\n"
        "- Если отель, комната или удобства не найдены, также будет ошибка.\n"
        "- Идентификаторы `hotel_id` и `room_id` должны быть положительными числами (≥1)."
    ),
)
async def edit_room(
    _: DepAccess,
    db: DepDB,
    room_data: EditRoom = Body(openapi_examples=openapi_room_examples),
    hotel_id: int = Path(ge=1),
    room_id: int = Path(ge=1),
):
    try:
        room_with = await RoomService(db).edit_room(room_data, hotel_id=hotel_id, room_id=room_id)
    except (
        RoomNotFoundException,
        HotelNotFoundException,
        FacilityNotFoundException,
        RoomMissingToHotelException,
    ) as exc:
        raise ObjectNotFoundHTTPException(exc)
    except ToBigIdException:
        raise ToBigIdHTTPException
    return {"status": "OK", "data": room_with}


# @router.put("/{hotel_id}/rooms_shymeiko/{room_id}")
async def update_room_shymeiko(
    db: DepDB,
    _: DepAccess,
    room_data: AddRoom,
    hotel_id: int = Path(ge=1),
    room_id: int = Path(ge=1),
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


# @router.patch("/{hotel_id}/rooms_shymeiko/{room_id}")
async def edit_room_shymeiko(
    _: DepAccess,
    db: DepDB,
    room_data: EditRoom,
    hotel_id: int = Path(ge=1),
    room_id: int = Path(ge=1),
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
