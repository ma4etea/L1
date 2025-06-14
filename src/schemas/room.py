from pydantic import BaseModel


class BaseRoom(BaseModel):
    title: str
    description: str | None = None
    price: int
    quantity: int

class AddRoom(BaseRoom):
    pass

class EditRoom(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None

class AddRoomToDb(BaseRoom):
    hotel_id: int


class Room(BaseRoom):
    id: int
