from datetime import timedelta, datetime, timezone

from fastapi import HTTPException
from passlib.context import CryptContext
import jwt

from src.config import settings


class Authservice:
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
        except jwt.exceptions.ExpiredSignatureError as e:
            raise HTTPException(401, f"{e}")
        except jwt.exceptions.InvalidSignatureError as e:
            raise HTTPException(401, f"{e}")
        return payload
