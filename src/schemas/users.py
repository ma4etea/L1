import re
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserReg(BaseModel):
    email: EmailStr
    password: Annotated[
        str, Field(min_length=8, max_length=20,
                   description="Пароль от 8 до 20 символов. "
                               "Должен содержать минимум 1 заглавную букву, "
                               "1 строчную, 1 цифру и 1 спецсимвол (!@#$%^&* и т.д.)"
                               "Например: Qwer123$"
                   )
    ]

    @field_validator("password", mode="before") # noqa ✅ Валидация pedantic!
    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        Проверяет, что пароль:
        - содержит хотя бы 1 заглавную букву
        - содержит хотя бы 1 строчную букву
        - содержит хотя бы 1 цифру
        - содержит хотя бы 1 специальный символ (!@#$%^&* и т. д.)
        """
        if not re.search(r"[A-Z]", password):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")
        if not re.search(r"[a-z]", password):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")
        if not re.search(r"\d", password):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ (!@#$%^&*)")
        return password


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str


class User(BaseModel):
    id: int
    email: EmailStr


class UserWithHashedPassword(User):
    hashed_password: str
