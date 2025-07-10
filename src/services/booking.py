from src.api.dependecy import DepAccess, DepPagination
from src.schemas.booking import BookingAdd, Booking, BookingToDB
from src.services.base import BaseService
from src.services.room import RoomService


class BookingService(BaseService):
    async def add_booking(self, user_id: DepAccess, data_booking: BookingAdd) -> Booking:
        room = await RoomService(self.db).check_room(room_id=data_booking.room_id)

        data_to_db = BookingToDB(**data_booking.model_dump(), user_id=user_id, price=room.price)
        booking = await self.db.bookings.add_booking(data_to_db)
        await self.db.commit()

        return booking

    async def get_bookings(self, pag: DepPagination)-> list[Booking]:
        offset = pag.per_page * pag.page - pag.per_page
        limit = pag.per_page
        bookings = await self.db.bookings.get_all(offset=offset, limit=limit)
        return bookings

    async def get_my_booking(self, user_id: int)-> list[Booking]:
        bookings = await self.db.bookings.get_all(user_id=user_id)
        return bookings

    async def get_my_bookings(self, user_id, pag):
        bookings = await self.db.bookings.get_my_bookings(user_id, pag)
        return bookings
