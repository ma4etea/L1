import logging
from datetime import date

from sqlalchemy import func, select

from src.database import engine
from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def get_available_rooms_ids(
        date_from: date,
        date_to: date,
        offset: int | None = None,
        limit: int | None = None,
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
        .filter(BookingsOrm.date_from <= date_to, BookingsOrm.date_to >= date_from)
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
            (RoomsOrm.quantity - func.coalesce(rooms_booked_count.c.booked, 0)).label("available"),
        )
        .select_from(RoomsOrm)
        .outerjoin(rooms_booked_count, RoomsOrm.id == rooms_booked_count.c.room_id)
    )
    rooms_available = rooms_available.cte("rooms_available")

    """ select * from rooms_available ra where ra.available > 0 """

    rooms_ids_from_hotel = select(RoomsOrm.id).select_from(RoomsOrm)
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


def check_rooms_available(
        date_from: date,
        date_to: date,
        room_id: int,
):
    """
    Проверяет, есть ли хотя бы одна доступная комната для бронирования по заданному `room_id`
    в интервале дат от `date_from` до `date_to` (включительно).

    Метод использует пересечение дат, то есть комната считается занятой, если:
        booking.date_from <= date_to AND booking.date_to >= date_from

    Алгоритм:
    1. Считает, сколько бронирований уже существует по данному `room_id`, пересекающихся с заданным диапазоном.
       (CTE: rooms_booked_count)
    2. Выполняет LEFT JOIN с таблицей `rooms`, чтобы получить общее количество комнат.
    3. Вычисляет доступность: `quantity - booked > 0`
       (то есть осталась хотя бы одна свободная комната).

    Параметры:
    :param date_from: Дата начала желаемого бронирования (включительно)
    :param date_to: Дата окончания желаемого бронирования (включительно)
    :param room_id: ID проверяемой комнаты

    Возвращает:
    SQLAlchemy Query, возвращающий булево значение `is_available`:
        - True, если хотя бы одна комната доступна
        - False, если все заняты
        - None, если комната не найдена

    Пример SQL-запроса, который будет сгенерирован:
        WITH rooms_booked_count AS (
            SELECT b.room_id, COUNT(*) AS booked
            FROM bookings b
            WHERE b.date_from <= :date_to AND b.date_to >= :date_from
              AND b.room_id = :room_id
            GROUP BY b.room_id
        )
        SELECT (r.quantity - COALESCE(rbc.booked, 0)) > 0 AS is_available
        FROM rooms r
        LEFT JOIN rooms_booked_count rbc ON r.id = rbc.room_id
        WHERE r.id = :room_id
    """
    b = BookingsOrm
    rooms_booked_count = (
        select(b.room_id, func.count("*").label("booked"))
        .select_from(b)
        .filter(b.date_from <= date_to, b.date_to >= date_from, b.room_id == room_id)
        .group_by(b.room_id)
        .cte("rooms_booked_count")
    )

    rbc = rooms_booked_count
    r = RoomsOrm
    query = (
        select((r.quantity - func.coalesce(rbc.c.booked, 0) > 0).label("is_available"))
        .select_from(r)
        .outerjoin(rbc, r.id == rbc.c.room_id)
        .filter(r.id == room_id)
    )
    logging.debug(f"Запрос в базу: \n{sql_debag(query)}")
    return query


def sql_debag(stmt) -> str:
    return stmt.compile(bind=engine, compile_kwargs={"literal_binds": True})
