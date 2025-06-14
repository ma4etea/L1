from fastapi import APIRouter, Path, HTTPException
from src.api.dependecy import AccessDep, DBDep
from src.schemas.room import AddRoom, AddRoomToDb, EditRoom

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(_: AccessDep, db: DBDep, hotel_id: int = Path()):
    return {
        "status": "OK",
        "data": await db.rooms.get_all(hotel_id=hotel_id),
    }


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room(
    _: AccessDep,
    db: DBDep,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    room = await db.rooms.get_one_none(hotel_id=hotel_id, id=room_id)
    if not room:
        raise HTTPException(404)
    return {"status": "OK", "data": room}


@router.post("/{hotel_id}/rooms")
async def add_room(_: AccessDep, db: DBDep, room_data: AddRoom, hotel_id: int = Path()):
    new_room_data = AddRoomToDb(**room_data.model_dump(), hotel_id=hotel_id)

    room = await db.rooms.add(new_room_data)
    await db.commit()

    return {
        "status": "OK",
        "data": room,
    }


@router.delete("/{hotel_id}/rooms/{room_id}")
async def remove_room(
    _: AccessDep,
    db: DBDep,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    await db.rooms.delete(hotel_id=hotel_id, id=room_id)
    await db.commit()

    return {"status": "OK"}


@router.put("/{hotel_id}/rooms/{room_id}")
async def update_room(
    db: DBDep,
    _: AccessDep,
    room_data: AddRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    await db.rooms.edit(room_data, hotel_id=hotel_id, id=room_id)
    await db.commit()

    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def edit_room(
    _: AccessDep,
    db: DBDep,
    room_data: EditRoom,
    hotel_id: int = Path(),
    room_id: int = Path(),
):
    await db.rooms.edit(room_data, exclude_unset=True, hotel_id=hotel_id, id=room_id)
    await db.commit()

    return {"status": "OK"}
