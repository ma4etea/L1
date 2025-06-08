import asyncio
import time

import uvicorn
from fastapi import FastAPI, Query, Body, Path

app = FastAPI()

hotels = [
    {"id": 1, "title": "sochi", "name": "hotel"},
    {"id": 2, "title": "дубай", "name": "motel"},
]

@app.get('/sync/{id}')
def sync_func(id: int):
    print(f'sync {id} начал: {time.time():.2f}')
    time.sleep(3)
    print(f'sync {id} закончил: {time.time():.2f}')

@app.get("/async/{id}")
async def async_func(id: int):
    print(f'async {id} начал: {time.time():.2f}')
    await asyncio.sleep(3)
    print(f'async {id} закончил: {time.time():.2f}')


@app.get("/hotels")
def get_hotels(
    id_: int | None = Query(None, description="ID"),
    title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = [
        hotel
        for hotel in hotels
        if title
        and hotel["title"].lower() == title.lower()
        and id_
        and hotel["id"] == id_
    ]
    if not hotels_:
        return hotels
    return hotels_


@app.post("/hotels")
def add_hotel(title: str = Body(), name: str | None = Body(None)):
    global hotels
    hotels.append({"id": len(hotels) + 1, "title": title, "name": name})
    return {"status": "ok"}


@app.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int = Path()):
    global hotels
    if len(hotels) < 1 or hotel_id < 1:
        return {"status": "error"}
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]

    return {"status": "delete"}


@app.patch("/hotels/{hotel_id}")
def edit_hotel(
    hotel_id: int = Path(),
    title: str | None = Body(None),
    name: str | None = Body(None),
):
    global hotels
    hotels_ = [hotel for hotel in hotels if hotel["id"] == hotel_id]
    hotel = hotels_[0]
    if hotel:
        if title:
            hotel["title"] = title
        if name:
            hotel["name"] = name
        return [hotel for hotel in hotels if hotel["id"] == hotel_id]
    return {"status": "error"}


@app.put("/hotels/{hotel_id}", summary="Изменение отеля", description='Только полное обновление')
def upd_hotel(hotel_id: int = Path(), title: str = Body(), name: str = Body()):
    global hotels
    hotels_ = [hotel for hotel in hotels if hotel["id"] == hotel_id]
    hotel = hotels_[0]
    print(hotel is hotels[hotel_id-1])
    if hotel:
        hotel["title"] = title
        hotel["name"] = name
        return [hotel for hotel in hotels if hotel["id"] == hotel_id]
    return {"status": "error"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=False, workers=None)

# uvicorn main:app
# fastapi dev main.py
# python main.py
