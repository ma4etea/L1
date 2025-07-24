from src.services.auth import AuthService


def test_create_access_token():
    user_id = 1
    jwt_token = AuthService().create_access_token(id=user_id)
    assert jwt_token and isinstance(jwt_token, str)
