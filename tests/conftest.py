import os
import uuid

import pytest
import requests

BASE_URL = os.getenv("BOOKER_BASE_URL", "https://restful-booker.herokuapp.com")
AUTH_CREDENTIALS = {"username": "admin", "password": "password123"}
REQUEST_TIMEOUT = 30


def build_booking(**overrides):
    booking = {
        "firstname": "QA",
        "lastname": f"Autotest-{uuid.uuid4().hex[:8]}",
        "totalprice": 1234,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-12-10", "checkout": "2026-12-15"},
        "additionalneeds": "None",
    }
    booking.update(overrides)
    return booking


@pytest.fixture(scope="session")
def session():
    client = requests.Session()
    client.headers.update({"Accept": "application/json"})
    yield client
    client.close()


@pytest.fixture(scope="session")
def auth_token(session):
    response = session.post(f"{BASE_URL}/auth", json=AUTH_CREDENTIALS, timeout=REQUEST_TIMEOUT)
    if response.status_code != 200 or "token" not in response.text:
        pytest.skip("Не удалось получить токен: API недоступно")
    return response.json()["token"]


@pytest.fixture()
def created_booking(session, auth_token):
    payload = build_booking()
    response = session.post(f"{BASE_URL}/booking", json=payload, timeout=REQUEST_TIMEOUT)
    assert response.status_code == 200, response.text
    booking_id = response.json()["bookingid"]
    yield {"id": booking_id, "payload": payload, "response": response.json()}
    session.delete(
        f"{BASE_URL}/booking/{booking_id}",
        headers={"Cookie": f"token={auth_token}"},
        timeout=REQUEST_TIMEOUT,
    )
