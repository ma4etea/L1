from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import BaseModel


class UsersOrm(BaseModel):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
