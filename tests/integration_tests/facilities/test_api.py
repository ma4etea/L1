from src.schemas.facilities import Facility


async def test_add_facility(auth_ac):
    json = {"title": "Скромный завтрак"}
    resp = await auth_ac.post("/facilities", json=json)
    assert resp.status_code == 200
    assert Facility(**resp.json()["data"])


# async def test_get_facilities(ac):
#     resp = await ac.get("/facilities/cached")
#     assert resp.status_code == 200
#     # assert Facility(**resp.json()['data'])
