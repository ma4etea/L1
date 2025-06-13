from typing import Annotated

from fastapi import Query, Depends, Request, HTTPException
from pydantic import BaseModel

from src.services.auth import Authservice


class Pagination(BaseModel):
    page: Annotated[int | None, Query(1, ge=1, description="какая страницы")]
    per_page: Annotated[int | None,  Query(None, ge=1, le=50, description="Сколько в странице")]

PaginationDep = Annotated[Pagination, Depends()]

def get_access_token(request: Request) -> str:
    cookies = request.cookies  # new_case получить куки
    access_token = cookies.get('access_token')
    if not access_token:
        raise HTTPException(status_code=401)
    return access_token

def get_payload_token (access_token: str = Depends(get_access_token)) -> int:
    payload = Authservice().jwt_decode(access_token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=404)
    return user_id

AccessDep = Annotated[int, Depends(get_payload_token)]