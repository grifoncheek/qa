import pytest

from conftest import AUTH_CREDENTIALS, BASE_URL, REQUEST_TIMEOUT

pytestmark = pytest.mark.integration



def test_ping_returns_201(session):
    response = session.get(f"{BASE_URL}/ping", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 201
    assert response.text == "Created"


def test_auth_with_valid_credentials_returns_token(session):
    response = session.post(f"{BASE_URL}/auth", json=AUTH_CREDENTIALS, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["token"], str)
    assert body["token"]


@pytest.mark.xfail(reason="BUG-10: API возвращает 200 вместо 401 при неверных данных", strict=False)
def test_auth_with_invalid_credentials_returns_401(session):
    response = session.post(
        f"{BASE_URL}/auth",
        json={"username": "admin", "password": "wrong-password"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 401
