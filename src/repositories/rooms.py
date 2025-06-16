from datetime import date

from sqlalchemy import func, select

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.schemas.room import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_available_rooms_shymeyko(
            self, offset: int, limit: int, date_from: date, date_to: date, hotel_id: int,
    ):
        """
        with rooms_booked_count as (
            select room_id, COUNT(*) as booked
            from bookings b
            where b.date_from <= '2025-06-17' and b.date_to >= '2025-06-09'
            group by room_id
        ),
        """
        rooms_booked_count = (
            select(BookingsOrm.room_id, func.count("*").label("booked"))
            .select_from(BookingsOrm)
            .filter(BookingsOrm.date_from <= date_from, BookingsOrm.date_to >= date_to)
            .group_by(BookingsOrm.room_id)
            .cte("rooms_booked_count")
        )

        """
        rooms_available as (
            select id as room_id, quantity-coalesce(booked, 0) as available
            from rooms r 
            left join rooms_booked_count rb on rb.room_id = r.id
        )
        """
        rooms_available = (
            select(
                RoomsOrm.id,
                RoomsOrm.title,
                RoomsOrm.description,
                RoomsOrm.price,
                RoomsOrm.id.label("room_id"),
                (
                        RoomsOrm.quantity - func.coalesce(rooms_booked_count.c.booked, 0)
                ).label("available"),
            )
            .select_from(RoomsOrm)
            .outerjoin(rooms_booked_count, RoomsOrm.id == rooms_booked_count.c.room_id)
        )
        rooms_available = rooms_available.cte("rooms_available")

        """ select * from rooms_available ra where ra.available > 0 """

        rooms_ids_from_hotel = (
            select(RoomsOrm.id)
            .select_from(RoomsOrm)
            .filter_by(hotel_id=hotel_id)
            .subquery("rooms_ids_from_hotel")
        )

        query = (
            select(rooms_available.c.room_id)
            .filter(rooms_available.c.available > 0, rooms_available.c.id.in_(rooms_ids_from_hotel))
            .offset(offset)
            .limit(limit)
            .order_by("id")
        )


        return await self.get_all(offset,limit ,RoomsOrm.id.in_(query))

        raise HTTPException(404)