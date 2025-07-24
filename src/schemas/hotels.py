from typing import Annotated

from pydantic import BaseModel, Field

from src.schemas.mixin.mixin import PatchValidatorMixin


class HotelAdd(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=100)]
    location: Annotated[str, Field(min_length=2, max_length=100)]


class Hotel(BaseModel):
    title: str
    location: str
    id: int


class HotelPatch(PatchValidatorMixin, BaseModel):
    title: Annotated[str, Field(None, min_length=2, max_length=100)]
    location: Annotated[str, Field(None, min_length=2, max_length=100)]
