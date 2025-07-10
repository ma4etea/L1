from datetime import date

from src.api.dependecy import DepPagination
from src.exceptions.exeptions import ObjectNotFoundException, RoomNotFoundException
from src.schemas.room import Room, RoomWith
from src.services.base import BaseService


class RoomService(BaseService):
    async def check_room(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc

    async def get_available_rooms(self, hotel_id: int, pag: DepPagination, date_from: date, date_to: date):
        offset = pag.per_page * pag.page - pag.per_page
        limit = pag.per_page
        rooms_available = await self.db.bookings.get_available_rooms(
            hotel_id=hotel_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
        )
        return rooms_available

    async def get_available_rooms_shymeyko(
            self,
            pag: DepPagination,
            date_from: date,
            date_to: date,
            hotel_id: int
    ):
        offset = pag.per_page * pag.page - pag.per_page
        limit = pag.per_page
        rooms_available = await self.db.rooms.get_available_rooms_shymeyko(
            hotel_id=hotel_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
        )
        return rooms_available

    async def get_rooms(self, hotel_id: int) -> list[RoomWith]:
        rooms_with = await self.db.rooms.get_rooms_with(hotel_id=hotel_id)
        return rooms_with

    async def get_room(self, hotel_id: int, room_id: int) -> RoomWith:
        try:
            room_with = await self.db.rooms.get_room_with(hotel_id=hotel_id, id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc
        return room_with
