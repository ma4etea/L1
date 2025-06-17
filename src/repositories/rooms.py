from datetime import date

from sqlalchemy import func, select

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.utils import get_available_rooms_ids
from src.schemas.room import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_available_rooms_shymeyko(
            self, offset: int, limit: int, date_from: date, date_to: date, hotel_id: int,
    ):
        return await self.get_all(offset, limit,
                                  RoomsOrm.id.in_(get_available_rooms_ids(offset, limit, date_from, date_to, hotel_id)))
