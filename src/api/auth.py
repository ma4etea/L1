from fastapi import APIRouter, HTTPException, Response, Request
from starlette.requests import cookie_parser

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
                               hashed_password=user.hashed_password):  # new проверка пароля
            raise HTTPException(status_code=401, detail="пароль не верный")
        access_token = Authservice().create_access_token(user_id=user.id)

        response.set_cookie("access_token", access_token)  # new добавление куки

        return {"access_token": access_token}


@router.get("test")
async def test(
  request: Request
):
    try:
        cookies = cookie_parser(request.headers.__getitem__('cookie'))
        print(cookies)
    except KeyError:
        raise HTTPException(401, "нет куков")
    access_token = cookies.get('access_token')
    return {"access_token": access_token}
