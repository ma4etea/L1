from fastapi import APIRouter, HTTPException, Response

from src.api.dependecy import DepAccess, DepDB
from src.exceptions.exeptions import ObjectAlreadyExistsException
from src.schemas.users import UserReg, UserAdd
from src.services.auth import Authservice

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register")
async def register_user(db: DepDB, data: UserReg):
    hashed_password = Authservice().pwd_context.hash(data.password)
    new_data_user = UserAdd(email=data.email, hashed_password=hashed_password)
    try:
        await db.auth.add(new_data_user)
    except ObjectAlreadyExistsException:
        raise HTTPException(409, "Пользователь уже существует")

    await db.commit()
    return {"status": "ok"}


@router.post("/login")
async def login_user(db: DepDB, data: UserReg, response: Response):
    user = await db.auth.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не зарегистрирован")
    if not Authservice().verify_password(
        plain_password=data.password, hashed_password=user.hashed_password
    ):  # new_case проверка пароля
        raise HTTPException(status_code=401, detail="пароль не верный")
    access_token = Authservice().create_access_token(user_id=user.id)

    response.set_cookie("access_token", access_token)  # new_case добавление куки

    return {"access_token": access_token}


@router.get("/me")
async def get_me(db: DepDB, user_id: DepAccess):
    user = await db.auth.get_one_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404)

    return user


@router.post("/logout")
async def logout(
    db: DepDB,
    response: Response,
    _: DepAccess,  # new_case переменная мусорка по конвенции python
):
    response.delete_cookie("access_token")
    return {"status": "ok"}
