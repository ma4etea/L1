from typing import Annotated

from fastapi import Query, Depends, Request, HTTPException
from jwt import ExpiredSignatureError, InvalidSignatureError
from pydantic import BaseModel

from src.api.http_exceptions.http_exeptions import InvalidTokenHTTPException, IncorrectTokenHTTPException, \
    ExpiredTokenHTTPException
from src.database import new_session
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class Pagination(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="какая страницы")]
    per_page: Annotated[int | None, Query(3, ge=1, le=50, description="Сколько в странице")]


DepPagination = Annotated[Pagination, Depends()]


def get_access_token(request: Request) -> str:
    cookies = request.cookies  # new_case получить куки
    access_token = cookies.get("access_token")
    if not access_token:
        raise InvalidTokenHTTPException
    return access_token


def get_payload_token(access_token: str = Depends(get_access_token)) -> int:
    try:
        payload = AuthService().jwt_decode(access_token)
    except ExpiredSignatureError:
        raise ExpiredTokenHTTPException
    except InvalidSignatureError:
        raise InvalidTokenHTTPException
    user_id = payload.get("user_id")
    if not user_id:
        raise IncorrectTokenHTTPException
    return user_id


DepAccess = Annotated[int, Depends(get_payload_token)]


def get_db():
    return DBManager(new_session)


async def get_db_manager():
    async with get_db() as db:
        yield db


DepDB = Annotated[DBManager, Depends(get_db_manager)]
