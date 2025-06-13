from fastapi import APIRouter
from passlib.context import CryptContext
from src.database import new_session
from src.repositories.auth import AuthRepository
from src.schemas.users import UserReg, UserAdd

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post("/register")
async def register_user(data: UserReg):
    hashed_password = pwd_context.hash(data.password)
    new_data_user = UserAdd(email=data.email, hashed_password=hashed_password)
    async with new_session() as session:
        await AuthRepository(session).add(new_data_user)
        await session.commit()
        return {"status": "ok"}
