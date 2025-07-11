from datetime import timedelta, datetime, timezone

from fastapi import HTTPException
from passlib.context import CryptContext
import jwt

from src.config import settings
from src.exceptions.exeptions import ObjectAlreadyExistsException, UserAlreadyExistsException, ObjectNotFoundException, \
    UserNotFoundException, InvalidCredentialsException
from src.schemas.users import UserReg, UserAdd, User
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(
            self,
            expires_delta: timedelta | None = timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            ),
            **data,
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def jwt_decode(self, access_token: str) -> dict:
        try:
            payload = jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.ExpiredSignatureError as exc:
            raise exc
        except jwt.exceptions.InvalidSignatureError as exc:
            raise exc
        return payload

    async def register_user(self, data: UserReg):
        hashed_password = self.pwd_context.hash(data.password)
        new_data_user = UserAdd(email=data.email, hashed_password=hashed_password)

        try:
            await self.db.auth.add(new_data_user)
            await self.db.commit()
        except ObjectAlreadyExistsException as exc:
            raise UserAlreadyExistsException from exc

    async def login_user(self, data: UserReg) -> str:
        try:
            user = await self.db.auth.get_user_with_hashed_password(email=data.email)
        except ObjectNotFoundException as exc:
            raise UserNotFoundException from exc
        if not self.verify_password(
                plain_password=data.password, hashed_password=user.hashed_password
        ):  # new_case проверка пароля
            raise InvalidCredentialsException
        return self.create_access_token(user_id=user.id)

    async def get_me(self, user_id: int) -> User:
        try:
            return await self.db.auth.get_one(id=user_id)
        except ObjectNotFoundException as exc:
            raise UserNotFoundException from exc