from src.exceptions.exeptions import ObjectNotFoundException, RoomNotFoundException, ToBigIdException
from src.schemas.room import Room
from src.services.base import BaseService


class RoomService(BaseService):
    async def check_room(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc