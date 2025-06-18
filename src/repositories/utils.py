from datetime import date

from sqlalchemy import func, select

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def get_available_rooms_ids(offset: int, limit: int, date_from: date, date_to: date, hotel_id: int = None, ):
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
            RoomsOrm.hotel_id,
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

    )
    if hotel_id:
        rooms_ids_from_hotel = rooms_ids_from_hotel.filter_by(hotel_id=hotel_id)
        rooms_ids_from_hotel = rooms_ids_from_hotel.subquery("rooms_ids_from_hotel")

    rooms_ids = (
        select(rooms_available.c.room_id)
        .select_from(rooms_available)
        .filter(rooms_available.c.available > 0, rooms_available.c.id.in_(rooms_ids_from_hotel))
        .offset(offset)
        .limit(limit)
        .order_by("id")
    )

    return rooms_ids
