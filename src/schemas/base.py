from datetime import date
from typing import Annotated

from pydantic import BaseModel as BaseSchema, Field

from src.schemas.mixin.mixin import DateFromTodayOrLaterMixin, DateRangeValidatorMixin


class DateBooking(DateFromTodayOrLaterMixin, DateRangeValidatorMixin, BaseSchema):
    date_from: Annotated[date, Field(description="Дата заезда, не раньше сегодняшнего дня")]
    date_to: Annotated[date, Field(description="Дата выезда, позже даты заезда ")]

    class Config:
        title = "Период бронирования"