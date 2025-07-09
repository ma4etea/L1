from datetime import date
from sqlalchemy import select, func
from sqlalchemy.exc import MultipleResultsFound, DBAPIError

from src.exceptions.exeptions import ObjectNotFoundException, UnexpectedResultFromDbException, NoAvailableRoom
from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.utils import check_rooms_available
from src.schemas.booking import RoomsAvailable, BookingToDB


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_available_rooms(
            self,
            offset: int,
            limit: int,
            date_from: date,
            date_to: date,
            hotel_id: int = None,
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
                (RoomsOrm.quantity - func.coalesce(rooms_booked_count.c.booked, 0)).label(
                    "available"
                ),
            )
            .select_from(RoomsOrm)
            .outerjoin(rooms_booked_count, RoomsOrm.id == rooms_booked_count.c.room_id)
        )
        if hotel_id:
            rooms_available = rooms_available.filter(RoomsOrm.hotel_id == hotel_id)
        rooms_available = rooms_available.cte("rooms_available")

        """ select * from rooms_available ra where ra.available > 0 """

        query = (
            select(rooms_available)
            .filter(rooms_available.c.available > 0)
            .offset(offset)
            .limit(limit)
            .order_by("id")
        )

        print(query.compile(compile_kwargs={"literal_binds": True}))

        result = await self.session.execute(query)
        rows = result.all()
        return [RoomsAvailable(**(row._mapping)) for row in rows]

    async def get_my_bookings(self, user_id: int, pag):
        """
        with booked_days as (
            select room_id, user_id, b.date_to - b.date_from as days, date_from, date_to
            from bookings b
            where b.user_id = 33
            )
        """
        b = BookingsOrm
        booked_days = (
            select(
                b.room_id,
                b.user_id,
                b.price,
                ((b.date_to - b.date_from).label("days")),
                b.date_from,
                b.date_to,
            )
            .select_from(b)
            .filter(b.user_id == user_id)
            .cte("booked_days")
        )

        """
        select room_id, user_id, hotel_id, date_from, date_to, title, description, days, price, days*price as total_cost 
        from booked_days bd 
        join rooms r on bd.room_id = r.id 
        order by bd.date_from
        """
        bd = booked_days
        r = RoomsOrm
        query = (
            select(
                bd.c.room_id,
                bd.c.user_id,
                r.hotel_id,
                bd.c.date_from,
                bd.c.date_to,
                r.title,
                r.description,
                bd.c.days,
                bd.c.price,
                (bd.c.days * bd.c.price).label("total_cost"),
            )
            .select_from(bd)
            .join(r, r.id == bd.c.room_id)
            .order_by(bd.c.date_to)
        )

        result = await self.session.execute(query)
        dicts = result.mappings().all()
        return dicts

    async def get_today_booking(self):
        query = select(self.model).filter(self.model.date_to == date.today())
        res = await self.session.execute(query)
        return [self.mapper.to_domain(model) for model in res.scalars().all()]

    async def add_booking(self, data: BookingToDB):

        try:
            res = await self.session.execute(
                check_rooms_available(
                    room_id=data.room_id, date_from=data.date_from, date_to=data.date_to
                )
            )
            is_available = res.scalar_one()
        except DBAPIError as exc:
            raise exc
        if not is_available:
            raise NoAvailableRoom
        model = await self.add(data)
        return model

