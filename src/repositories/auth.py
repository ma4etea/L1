from sqlalchemy import select

from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.schemas.users import User, UserWithHashedPassword


class AuthRepository(BaseRepository):
    model = UsersOrm
    schema = User

    async def get_user_with_hashed_password(self, email):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        user = result.scalars().one_or_none()
        if not user:
            return None
        return UserWithHashedPassword.model_validate(user, from_attributes=True)