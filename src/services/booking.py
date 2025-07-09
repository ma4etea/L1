from src.api.dependecy import DepAccess
from src.exceptions.exeptions import UnexpectedResultFromDbException, ObjectNotFoundException
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


