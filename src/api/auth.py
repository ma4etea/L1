from fastapi import APIRouter, HTTPException, Response, Request
from starlette.requests import cookie_parser

from src.api.dependecy import AccessDep
from src.database import new_session
from src.repositories.auth import AuthRepository
from src.schemas.users import UserReg, UserAdd
from src.services.auth import Authservice

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register")
async def register_user(data: UserReg):
    hashed_password = Authservice().pwd_context.hash(data.password)
    new_data_user = UserAdd(email=data.email, hashed_password=hashed_password)
    async with new_session() as session:
        await AuthRepository(session).add(new_data_user)
        await session.commit()
        return {"status": "ok"}


@router.post("/login")
async def login_user(
        data: UserReg,
        response: Response
):
    async with new_session() as session:
        user = await AuthRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не зарегистрирован")
        if not Authservice().verify_password(plain_password=data.password,
                                             hashed_password=user.hashed_password):  # new_case проверка пароля
            raise HTTPException(status_code=401, detail="пароль не верный")
        access_token = Authservice().create_access_token(user_id=user.id)

        response.set_cookie("access_token", access_token)  # new_case добавление куки

        return {"access_token": access_token}


@router.get("/me")
async def get_me(
        user_id: AccessDep
):
    async with new_session() as session:
        user = await AuthRepository(session).get_one_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404)

    return user


@router.post("/logout")
async def logout(
        response: Response,
        _: AccessDep  # new_case переменная мусорка по конвенции python
):
    response.delete_cookie("access_token")
    return {"status": "ok"}
