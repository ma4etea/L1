from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.schemas.users import UserAdd


class AuthRepository(BaseRepository):
    model = UsersOrm
    schema = UserAdd