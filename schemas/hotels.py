from fastapi import Body
from pydantic import BaseModel


class Hotel(BaseModel):
    title: str
    name: str

class HotelPatch(BaseModel):
    title: str | None = None
    name: str | None = None
