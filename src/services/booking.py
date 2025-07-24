
from src.api.dependecy import DepAccess
from src.exceptions.exсeptions import BookingsNotFoundException
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

    async def get_bookings(self, page: int, per_page: int) -> list[Booking]:
        total = await self.db.bookings.get_total()
        if total <= 0:
            raise BookingsNotFoundException
        offset, limit = self.get_pagination_with_check(
            page=page, per_page=per_page, check_total=total
        )
        bookings = await self.db.bookings.get_all(offset=offset, limit=limit)
        if not bookings:
            raise BookingsNotFoundException
        return bookings

    async def get_my_bookings(self, user_id: int, page: int, per_page: int) -> list[Booking]:
        total = await self.db.bookings.get_total(user_id=user_id)
        if total <= 0:
            raise BookingsNotFoundException
        offset, limit = self.get_pagination_with_check(
            page=page, per_page=per_page, check_total=total
        )
        bookings = await self.db.bookings.get_all(user_id=user_id, offset=offset, limit=limit)
        if not bookings:
            raise BookingsNotFoundException
        return bookings

    async def get_my_bookings_(self, user_id, pag):
        bookings = await self.db.bookings.get_my_bookings(user_id, pag)
        return bookings
