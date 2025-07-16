from typing import Annotated

from pydantic import BaseModel, Field

from src.schemas.mixin.mixin import PatchValidatorMixin, RemoveNullFieldsMixin, RejectNullFieldsMixin


class HotelAdd(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=100)]
    location: Annotated[str, Field(min_length=2, max_length=100)]


class Hotel(BaseModel):
    title: str
    location: str
    id: int


class HotelPatch(RejectNullFieldsMixin, PatchValidatorMixin, BaseModel):
    title: Annotated[str | None, Field(None, min_length=2, max_length=100)]
    location: Annotated[str | None, Field(None, min_length=2, max_length=100)]