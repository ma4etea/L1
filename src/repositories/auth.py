from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import AuthDataMapper
from src.schemas.users import User, UserWithHashedPassword


class AuthRepository(BaseRepository):
    model = UsersOrm
    mapper = AuthDataMapper

    async def get_user_with_hashed_password(self, email):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if not model:
            return None
        return UserWithHashedPassword.model_validate(model, from_attributes=True)