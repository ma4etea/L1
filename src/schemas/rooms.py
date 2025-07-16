from typing import Annotated

from pydantic import BaseModel, Field

from src.schemas.facilities import Facility
from src.schemas.mixin.mixin import PatchValidatorMixin


class BaseRoom(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int


class AddRoom(BaseModel):
    title: Annotated[str, Field(min_length=2, max_length=100)]
    description: Annotated[str | None, Field(min_length=2, max_length=100)]
    price: Annotated[int, Field(ge=0)]
    quantity: Annotated[int, Field(ge=1)]
    facilities_ids: list[Annotated[int, Field(ge=1)]]


class EditRoom(PatchValidatorMixin, BaseModel):
    title: Annotated[str, Field(None, min_length=2, max_length=100)]
    description: Annotated[str | None, Field(None, min_length=2, max_length=100)]
    price: Annotated[int, Field(None, ge=0)]
    quantity: Annotated[int, Field(None, ge=1)]
    facilities_ids: list[Annotated[int, Field(ge=1)]]= None


class AddRoomToDb(BaseRoom):
    hotel_id: int


class Room(BaseRoom):
    id: int

class RoomWith(BaseRoom):
    facilities: list[Facility]
    id: int
