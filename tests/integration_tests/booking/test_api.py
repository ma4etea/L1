import pytest



@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2026-07-10", "2026-07-11", 200),
        (1, "2026-07-10", "2026-07-11", 200),
        (1, "2026-07-10", "2026-07-11", 200),
        (1, "2026-07-10", "2026-07-11", 200),
        (1, "2026-07-10", "2026-07-11", 200),
        (1, "2026-07-10", "2026-07-11", 409),
        (0, "2026-07-12", "2026-07-14", 422),
    ])
async def test_booking(room_id, date_from, date_to, status_code, auth_ac, db):
    booking = {
        "date_from": date_from,
        "date_to": date_to,
        "room_id": room_id
    }

    resp = await auth_ac.post("/bookings", json=booking)
    assert resp.status_code == status_code


is_runed = False


# new_case: так же можно сделать на scope="module", но тогда нужно будет внутри создать свою db_, так как db из conftest живет на scope="function"
@pytest.fixture(scope="function")
async def delete_all_booking(db):
    global is_runed
    if not is_runed:
        await db.bookings.delete_bulk()
        await db.commit()
        is_runed = True

@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code, quantity_booking",
    [
        (1, "2026-07-10", "2026-07-11", 200, 1),
        (1, "2026-07-10", "2026-07-11", 200, 2),
        (1, "2026-07-10", "2026-07-11", 200, 3),
    ])
async def test_add_and_get_bookings(room_id, date_from, date_to, status_code, quantity_booking, delete_all_booking,
                                    auth_ac):
    booking = {
        "date_from": date_from,
        "date_to": date_to,
        "room_id": room_id
    }
    resp = await auth_ac.post("/bookings", json=booking)
    assert resp.status_code == status_code

    resp = await auth_ac.get("/bookings/me")
    assert resp.status_code == status_code
    print("ПРОВЕРКА", resp.json()["data"])
    assert len((resp.json()["data"])) == quantity_booking
