from fastapi import APIRouter, Response

from src.api.dependecy import DepAccess, DepDB
from src.exceptions.exeptions import UserAlreadyExistsException, UserNotFoundException, \
    InvalidCredentialsException
from src.api.http_exceptions.http_exeptions import UserAlreadyExistsHTTPException, UserNotFoundHTTPException, \
    InvalidCredentialsHTTPException
from src.schemas.users import UserReg
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register")
async def register_user(db: DepDB, data: UserReg):
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistsException:
        raise UserAlreadyExistsHTTPException
    return {"status": "ok"}


@router.post("/login")
async def login_user(db: DepDB, data: UserReg, response: Response):
    try:
        access_token = await AuthService(db).login_user(data)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except InvalidCredentialsException:
        raise InvalidCredentialsHTTPException
    response.set_cookie("access_token", access_token)  # new_case добавление куки
    return {"access_token": access_token}


@router.get("/me")
async def get_me(db: DepDB, user_id: DepAccess):
    try:
        return await AuthService(db).get_me(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException


@router.post("/logout")
async def logout(
    response: Response,
    _: DepAccess,  # new_case переменная мусорка по конвенции python
):
    response.delete_cookie("access_token")
    return {"status": "ok"}
