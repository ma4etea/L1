import uvicorn
from fastapi import FastAPI, Query, Body, Path

app = FastAPI()

hotels = [
    {"id": 1, "title": "sochi", "name": "hotel"},
    {"id": 2, "title": "дубай", "name": "motel"},
]


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
    hotel = [hotel for hotel in hotels if hotel["id"] == hotel_id]
    if hotel:
        if title:
            hotel[0]["title"] = title
        if name:
            hotel[0]["name"] = name
        return hotel
    return {"status": "error"}


@app.put("/hotels/{hotel_id}")
def edit_hotel(hotel_id: int = Path(), title: str = Body(), name: str = Body()):
    hotel = [hotel for hotel in hotels if hotel["id"] == hotel_id]
    if hotel:
        hotel[0]["title"] = title
        hotel[0]["name"] = name
        return hotel
    return {"status": "error"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

# uvicorn main:app
# fastapi dev main.py
# python main.py
