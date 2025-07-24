import logging
from datetime import date

from sqlalchemy import func, select

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import HotelDataMapper
from src.repositories.utils import get_available_rooms_ids, sql_debag


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_available_hotels(
        self, title, location, offset, limit, date_from: date, date_to: date
    ):
        hotels_ids = select(self.model.id)

        if title:
            hotels_ids = hotels_ids.where(HotelsOrm.title.ilike(f"%{title.strip()}%"))

        if location:
            hotels_ids = hotels_ids.where(
                func.lower(HotelsOrm.location).contains(location.strip().lower())
            )

        rooms = (
            select(RoomsOrm.hotel_id)
            .distinct()
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(get_available_rooms_ids(date_from=date_from, date_to=date_to)))
        )

        hotels_ids = hotels_ids.filter(self.model.id == rooms.c.hotel_id)

        logging.debug(f"Запрос в базу: \n{sql_debag(hotels_ids)}")

        return await self.get_all(offset, limit, HotelsOrm.id.in_(hotels_ids))
