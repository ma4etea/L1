from datetime import date

from src.api.dependecy import DepPagination
from src.exceptions.exeptions import ObjectNotFoundException, RoomNotFoundException, FacilityNotFoundException
from src.exceptions.utils import check_data_from_after_date_to_http_exc
from src.schemas.facilities import AddRoomsFacilities
from src.schemas.rooms import Room, RoomWith, AddRoomToDb, AddRoom
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def check_room(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc

    async def get_available_rooms(self, hotel_id: int, pag: DepPagination, date_from: date, date_to: date):
        check_data_from_after_date_to_http_exc(date_from=date_from, date_to=date_to)
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
        check_data_from_after_date_to_http_exc(date_from=date_from, date_to=date_to)
        offset = pag.per_page * pag.page - pag.per_page
        limit = pag.per_page
        rooms_available = await self.db.rooms.get_available_rooms_shymeyko(
            hotel_id=hotel_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
        )
        return rooms_available

    async def get_rooms(self, hotel_id: int) -> list[RoomWith]:
        await HotelService(self.db).check_hotel(hotel_id)
        rooms_with = await self.db.rooms.get_rooms_with(hotel_id=hotel_id)
        if not rooms_with:
            raise RoomNotFoundException
        return rooms_with

    async def get_room(self, hotel_id: int, room_id: int) -> RoomWith:
        try:
            room_with = await self.db.rooms.get_room_with(hotel_id=hotel_id, id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc
        return room_with

    async def remove_room(self, hotel_id:int, room_id:int) -> None:
        await HotelService(self.db).check_hotel(hotel_id=hotel_id)
        await self.check_room(room_id=room_id)
        await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        await self.db.commit()

    async def create_room(self, hotel_id: int, room_data: AddRoom) -> Room:
        await HotelService(self.db).check_hotel(hotel_id)
        new_room_data = AddRoomToDb(**room_data.model_dump(), hotel_id=hotel_id)
        room: Room = await self.db.rooms.add(new_room_data)

        if room_data.facilities_ids:
            try:
                await self.db.rooms_facilities.add_bulk(
                    [AddRoomsFacilities(room_id=room.id, facility_id=id_) for id_ in room_data.facilities_ids]
                )
            except ObjectNotFoundException as exc:
                raise FacilityNotFoundException from exc

        await self.db.commit()
        return room

