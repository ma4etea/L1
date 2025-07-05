from src.schemas.booking import Booking


async def test_booking(auth_ac, db):
    rooms = await db.rooms.get_all()

    booking = {
        "date_from": "2025-07-07",
        "date_to": "2025-07-05",
        "room_id": rooms[0].id,
    }

    resp = await auth_ac.post("/bookings", json=booking)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert Booking.model_validate(resp.json()["data"])
