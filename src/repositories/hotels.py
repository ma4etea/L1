from datetime import date

from sqlalchemy import func, select

from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.utils import get_available_rooms_ids
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsOrm
    schema = Hotel

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
            .filter(
                RoomsOrm.id.in_(
                    get_available_rooms_ids(
                        offset=offset, limit=limit, date_from=date_from, date_to=date_to
                    )
                )
            )
        )

        hotels_ids = hotels_ids.filter(self.model.id == rooms.c.hotel_id)

        # print(query.compile(compile_kwargs={"literal_binds": True}))

        return await self.get_all(None, None, HotelsOrm.id.in_(hotels_ids))
