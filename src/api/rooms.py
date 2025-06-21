from fastapi import APIRouter, Path, HTTPException
from src.api.dependecy import DepAccess, DepDB
from src.schemas.facilities import AddRoomsFacilities
from src.schemas.room import AddRoom, AddRoomToDb, EditRoom

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(_: DepAccess, db: DepDB, hotel_id: int = Path()):
    return {
        "status": "OK",
        "data": await db.rooms.get_all(hotel_id=hotel_id),
    }


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    _: DepAccess,
    db: DepDB,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    room = await db.rooms.get_one_none(hotel_id=hotel_id, id=room_id)
    if not room:
        raise HTTPException(404)
    return {"status": "OK", "data": room}


@router.post("/{hotel_id}/rooms")
async def create_room(_: DepAccess, db: DepDB, room_data: AddRoom, hotel_id: int = Path()):
    new_room_data = AddRoomToDb(**room_data.model_dump(), hotel_id=hotel_id)

    room = await db.rooms.add(new_room_data)

    await db.rooms_facilities.add_bulk([AddRoomsFacilities(room_id=room.id, facility_id=id_) for id_ in room_data.facilities_ids])

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
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()

    return {"status": "OK"}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
    db: DepDB,
    _: DepAccess,
    room_data: AddRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    room = await db.rooms.edit_room(room_data, hotel_id=hotel_id, room_id=room_id)
    await db.commit()

    return {"status": "OK", "data": room}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def edit_room(
    _: DepAccess,
    db: DepDB,
    room_data: EditRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    room = await db.rooms.edit_room(room_data, exclude_unset=True, hotel_id=hotel_id, room_id=room_id)
    await db.commit()

    return {"status": "OK","data": room}
