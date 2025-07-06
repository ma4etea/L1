from typing import Annotated

from fastapi import Body
from pydantic import BaseModel as BaseSchema


class AddFacility(BaseSchema):
    title: Annotated[
        str,
        Body(
            min_length=0,
            max_length=100,
        ),
    ]


class Facility(BaseSchema):
    id: int
    title: str


class AddRoomsFacilities(BaseSchema):
    room_id: int
    facility_id: int


class RoomsFacilities(BaseSchema):
    id: int
