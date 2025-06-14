from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.schemas.room import Room


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room