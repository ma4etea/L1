from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesORM
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.booking import Booking
from src.schemas.facilities import Facility, RoomsFacilities
from src.schemas.hotels import Hotel
from src.schemas.room import Room
from src.schemas.users import User


class AuthDataMapper(DataMapper):
    model = UsersOrm
    schema = User


class BookingDataMapper(DataMapper):
    model = BookingsOrm
    schema = Booking


class FacilityDataMapper(DataMapper):
    model = FacilitiesOrm
    schema = Facility

class RoomFacilityDataMapper(DataMapper):
    model = RoomsFacilitiesORM
    schema = RoomsFacilities

class HotelDataMapper(DataMapper):
    model = HotelsOrm
    schema = Hotel

class RoomDataMapper(DataMapper):
    model = RoomsOrm
    schema = Room


