from typing import Annotated

from fastapi import Body
from pydantic import BaseModel as BaseSchema, Field


class AddFacility(BaseSchema):
    title: Annotated[
        str,
        Body(
            min_length=2,
            max_length=100,
        ),
    ]


class Facility(BaseSchema):
    id: int
    title: str


class AddRoomsFacilities(BaseSchema):
    room_id: Annotated[int, Field(ge=1)]
    facility_id: Annotated[int, Field(ge=1)]


class RoomsFacilities(BaseSchema):
    id: int
