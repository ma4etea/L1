
from src.services.auth import Authservice


def test_create_access_token():
    user_id: int = 1
    jwt_token = Authservice().create_access_token(id=user_id)
    assert jwt_token and isinstance(jwt_token, str)

    payload = Authservice().jwt_decode(jwt_token)
    assert payload["id"] == user_id