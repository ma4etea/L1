from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.schemas.booking import Booking


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    schema = Booking
