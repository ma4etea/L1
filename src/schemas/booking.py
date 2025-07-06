from pydantic import BaseModel
from datetime import date


class BookingAdd(BaseModel):
    date_from: date
    date_to: date
    room_id: int


class BookingToDB(BookingAdd):
    user_id: int
    price: int


class Booking(BookingAdd):
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
