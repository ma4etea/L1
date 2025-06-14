from fastapi import APIRouter, Path, HTTPException

from src.api.dependecy import AccessDep
from src.database import new_session
from src.repositories.rooms import RoomsRepository
from src.schemas.room import AddRoom, AddRoomToDb, EditRoom

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(_: AccessDep, hotel_id: int = Path()):
    async with new_session() as session:
        return {
            "status": "OK",
            "data": await RoomsRepository(session).get_all(hotel_id=hotel_id),
        }


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    _: AccessDep,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    async with new_session() as session:
        room = await RoomsRepository(session).get_one_none(hotel_id=hotel_id, id=room_id)
        if not room:
            raise HTTPException(404)
        return {"status": "OK", "data": room}


@router.post("/{hotel_id}/rooms")
async def add_room(_: AccessDep, room_data: AddRoom, hotel_id: int = Path()):
    new_room_data = AddRoomToDb(**room_data.model_dump(), hotel_id=hotel_id)

    async with new_session() as session:
        room = await RoomsRepository(session).add(new_room_data)
        await session.commit()
    return {
        "status": "OK",
        "data": room,
    }


@router.delete("/{hotel_id}/rooms/{room_id}")
async def remove_room(
    _: AccessDep,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    async with new_session() as session:
        await RoomsRepository(session).delete(hotel_id=hotel_id, id=room_id)
        await session.commit()
    return {"status": "OK"}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
    room_data: AddRoom,
    _: AccessDep,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    async with new_session() as session:
        await RoomsRepository(session).edit(room_data, hotel_id=hotel_id, id=room_id)
        await session.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def edit_room(
    room_data: EditRoom,
    _: AccessDep,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    async with new_session() as session:
        await RoomsRepository(session).edit(
            room_data, exclude_unset=True, hotel_id=hotel_id, id=room_id
        )
        await session.commit()
    return {"status": "OK"}
