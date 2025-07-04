async def test_get_hotels(ac):
    params = {
        "date_to": "2025-06-01",
        "date_from": "2025-06-29"
    }
    result = await ac.get("hotels", params=params)


