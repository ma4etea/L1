from src.models.facilities import FacilitiesOrm, RoomsFacilitiesORM
from src.repositories.base import BaseRepository
from src.schemas.facilities import Facility, AddRoomsFacilities


class FacilitiesRepository(BaseRepository):
    model = FacilitiesOrm
    schema = Facility


class RoomsFacilitiesRepository(BaseRepository):
    model = RoomsFacilitiesORM
    schema = AddRoomsFacilities