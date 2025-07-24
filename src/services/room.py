from collections import defaultdict
from datetime import date


from src.api.dependecy import DepPagination
from src.exceptions.exсeptions import (
    ObjectNotFoundException,
    RoomNotFoundException,
    FacilityNotFoundException,
    ObjectHaveForeignKeyException,
    RoomHaveBookingException,
    RoomMissingToHotelException,
)
from src.exceptions.utils import check_data_from_after_date_to_http_exc
from src.schemas.facilities import AddRoomsFacilities
from src.schemas.rooms import Room, RoomWith, AddRoomToDb, AddRoom, EditRoom
from src.services.base import BaseService
from src.services.facility import FacilityService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def check_room(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException(room_id) from exc

    async def get_available_rooms(
        self, hotel_id: int | None, page: int, per_page: int, date_from: date, date_to: date
    ):
        if hotel_id:
            await HotelService(self.db).check_hotel(hotel_id)

        offset, limit = self.get_pagination_with_check(page, per_page)
        rooms_available = await self.db.bookings.get_available_rooms(
            hotel_id=hotel_id, offset=offset, limit=limit, date_from=date_from, date_to=date_to
        )
        if not rooms_available:
            raise RoomNotFoundException
        room_ids = [room["id"] for room in rooms_available]
        rooms_facilities = await self.db.rooms_facilities.get_facilities_with_by_rooms_ids(room_ids)

        # группируем facilities по room_id
        facilities_map = defaultdict(list)
        for facility in rooms_facilities:
            facilities_map[facility["room_id"]].append(
                {"id": facility["id"], "title": facility["title"]}
            )

        # назначаем каждому room его facilities
        for room in rooms_available:
            room["facilities"] = facilities_map.get(room["id"], [])

        return rooms_available

    async def get_available_rooms_shymeyko(
        self, pag: DepPagination, date_from: date, date_to: date, hotel_id: int
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
        await HotelService(self.db).check_hotel(hotel_id)
        try:
            room_with = await self.db.rooms.get_room_with(hotel_id=hotel_id, id=room_id)
        except ObjectNotFoundException as exc:
            raise RoomNotFoundException from exc
        return room_with

    async def remove_room(self, hotel_id: int, room_id: int) -> None:
        await HotelService(self.db).check_hotel(hotel_id=hotel_id)
        await self.check_room(room_id=room_id)
        try:
            await self.db.rooms.delete(hotel_id=hotel_id, id=room_id)
        except ObjectHaveForeignKeyException:
            raise RoomHaveBookingException
        except ObjectNotFoundException:
            raise RoomMissingToHotelException
        await self.db.commit()

    async def create_room(self, hotel_id: int, room_data: AddRoom) -> RoomWith:
        await HotelService(self.db).check_hotel(hotel_id)
        new_room_data = AddRoomToDb(**room_data.model_dump(), hotel_id=hotel_id)
        room: Room = await self.db.rooms.add(new_room_data)
        await FacilityService(self.db).check_facilities(room_data.facilities_ids)
        if room_data.facilities_ids:
            try:
                await self.db.rooms_facilities.add_bulk(
                    [
                        AddRoomsFacilities(room_id=room.id, facility_id=id_)
                        for id_ in room_data.facilities_ids
                    ]
                )
            except ObjectNotFoundException as exc:
                raise FacilityNotFoundException from exc

        room_with: RoomWith = await self.db.rooms.get_room_with(id=room.id)
        await self.db.commit()
        return room_with

    async def update_room(self, room_data: AddRoom, hotel_id: int, room_id: int) -> RoomWith:
        await HotelService(self.db).check_hotel(hotel_id)
        await self.check_room(room_id)
        await FacilityService(self.db).check_facilities(room_data.facilities_ids)
        try:
            await self.db.rooms.edit_room(room_data, hotel_id=hotel_id, room_id=room_id)
        except ObjectNotFoundException:
            raise RoomMissingToHotelException
        room_with: RoomWith = await self.db.rooms.get_room_with(id=room_id)
        await self.db.commit()
        return room_with

    async def edit_room(self, room_data: EditRoom, hotel_id: int, room_id: int) -> RoomWith:
        await HotelService(self.db).check_hotel(hotel_id)
        await self.check_room(room_id)
        if room_data.facilities_ids:
            await FacilityService(self.db).check_facilities(room_data.facilities_ids)
        try:
            await self.db.rooms.edit_room(
                room_data, exclude_unset=True, hotel_id=hotel_id, room_id=room_id
            )
        except ObjectNotFoundException:
            raise RoomMissingToHotelException
        room_with: RoomWith = await self.db.rooms.get_room_with(id=room_id)
        await self.db.commit()
        return room_with
