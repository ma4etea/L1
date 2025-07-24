import logging

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.exceptions.exсeptions import ObjectNotFoundException
from src.models.users import UsersOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import AuthDataMapper
from src.schemas.users import UserWithHashedPassword
from src.utils.logger_utils import exc_log_string


class AuthRepository(BaseRepository):
    model = UsersOrm
    mapper = AuthDataMapper

    async def get_user_with_hashed_password(self, email):
        query = select(self.model).filter_by(email=email)
        try:
            result = await self.session.execute(query)
            model = result.scalar_one()
            return UserWithHashedPassword.model_validate(model, from_attributes=True)
        except NoResultFound as exc:
            logging.error(exc_log_string(exc))
            raise ObjectNotFoundException from exc
