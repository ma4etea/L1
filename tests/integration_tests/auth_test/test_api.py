"""
Пошаговое тестирование API аутентификации:

1. POST /auth/register
   - Ожидаемый статус: 200
   - Если успешно, переходим к следующему шагу.

2. POST /auth/login
   - Проверить наличие и изменение cookies до и после логина.

3. GET /auth/me
   - Сверить email, полученный от API, с ожидаемым.

4. POST /auth/logout
   - Проверить, что cookie с токеном удалено (пользователь разлогинен).
"""

import pytest


@pytest.mark.parametrize(
    "creds, status_code",
    [
        ({"email": "user@example.com", "password": "!Qwe1234"}, 200),
        ({"email": "user@example.com", "password": "!Qwe1234"}, 409),
        ({"email": "new-user@example.com", "password": "!Qwe1234"}, 200),
        ({"email": "new-user@example", "password": "!Qwe1234"}, 422),
        ({"email": "new-user", "password": "!Qwe1234"}, 422),
    ],
)
async def test_auth(creds, status_code, ac):
    resp_reg = await ac.post("/auth/register", json=creds)
    assert resp_reg.status_code == status_code

    if resp_reg.status_code == 200:
        assert not ac.cookies
        resp_login = await ac.post("/auth/login", json=creds)
        assert resp_login.status_code == 200
        assert ac.cookies
        assert "access_token" in resp_login.json()
        assert set(resp_login.json()) == {
            "access_token",
        }  # new_case: Супер кейс как убедится что только определенные ключи есть в словаре

        resp_me = await ac.get("/auth/me")
        assert resp_me.status_code == 200
        assert resp_me.json()["email"] == creds["email"]

        assert ac.cookies
        resp_logout = await ac.post("/auth/logout")
        assert resp_logout.status_code == 200
        assert not ac.cookies
