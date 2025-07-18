from typing import Annotated

from pydantic import BaseModel, Field
from datetime import date

from src.schemas.facilities import Facility
from src.schemas.mixin.mixin import DateRangeValidatorMixin, DateFromTodayOrLaterMixin


class BookingAdd(DateFromTodayOrLaterMixin, DateRangeValidatorMixin, BaseModel):
    date_from: Annotated[date, Field(description="Дата заезда, не раньше сегодняшнего дня")]
    date_to: Annotated[date, Field(description="Дата выезда, позже даты заезда ")]
    room_id: Annotated[int, Field(ge=1)]


class BookingToDB(BookingAdd):
    user_id: int
    price: int


class Booking(BaseModel):
    date_from: date
    date_to: date
    id: int
    price: int
    total_cost: int


class RoomsAvailable(BaseModel):
    id: int
    title: str
    description: str
    price: int
    room_id: int
    available: int
    facilities: list[Facility] = []
