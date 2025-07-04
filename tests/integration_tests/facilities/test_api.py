from src.schemas.facilities import Facility


async def test_add_facility(ac):
    json = {
        "title": "Скромный завтрак"
    }
    resp = await ac.post("/facilities", json=json)
    assert resp.status_code == 200
    assert Facility(**resp.json()['data'])