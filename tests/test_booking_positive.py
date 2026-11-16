import pytest

from conftest import BASE_URL, REQUEST_TIMEOUT, build_booking

pytestmark = pytest.mark.integration



def test_create_booking_returns_booking_id(session, created_booking):
    body = created_booking["response"]

    assert isinstance(body["bookingid"], int)
    assert body["bookingid"] > 0
    assert body["booking"]["firstname"] == "QA"
    assert body["booking"]["lastname"] == created_booking["payload"]["lastname"]
    assert body["booking"]["totalprice"] == 1234
    assert body["booking"]["depositpaid"] is True
    assert body["booking"]["bookingdates"] == {"checkin": "2026-12-10", "checkout": "2026-12-15"}


def test_get_booking_by_id(session, created_booking):
    response = session.get(f"{BASE_URL}/booking/{created_booking['id']}", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == created_booking["payload"]["firstname"]
    assert body["lastname"] == created_booking["payload"]["lastname"]
    assert body["totalprice"] == 1234


def test_get_all_bookings_contains_created_id(session, created_booking):
    response = session.get(f"{BASE_URL}/booking", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    ids = [item["bookingid"] for item in response.json()]
    assert created_booking["id"] in ids


def test_update_booking_put(session, auth_token, created_booking):
    updated = build_booking(lastname=created_booking["payload"]["lastname"], firstname="QA Updated", totalprice=2000)
    updated["bookingdates"] = {"checkin": "2026-12-11", "checkout": "2026-12-16"}

    response = session.put(
        f"{BASE_URL}/booking/{created_booking['id']}",
        json=updated,
        headers={"Cookie": f"token={auth_token}"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == "QA Updated"
    assert body["totalprice"] == 2000
    assert body["bookingdates"]["checkin"] == "2026-12-11"

    check = session.get(f"{BASE_URL}/booking/{created_booking['id']}", timeout=REQUEST_TIMEOUT)
    assert check.json()["firstname"] == "QA Updated"


def test_partial_update_booking_patch(session, auth_token, created_booking):
    response = session.patch(
        f"{BASE_URL}/booking/{created_booking['id']}",
        json={"firstname": "QA Patched"},
        headers={"Cookie": f"token={auth_token}"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firstname"] == "QA Patched"
    assert body["lastname"] == created_booking["payload"]["lastname"]
    assert body["totalprice"] == 1234


def test_filter_by_lastname_returns_created_booking(session, created_booking):
    response = session.get(
        f"{BASE_URL}/booking",
        params={"lastname": created_booking["payload"]["lastname"]},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200
    ids = [item["bookingid"] for item in response.json()]
    assert ids == [created_booking["id"]]


def test_filter_without_matches_returns_empty_list(session):
    response = session.get(
        f"{BASE_URL}/booking",
        params={"lastname": "QA-no-such-client-2026"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 200
    assert response.json() == []


def test_delete_booking_then_get_returns_404(session, auth_token, created_booking):
    delete = session.delete(
        f"{BASE_URL}/booking/{created_booking['id']}",
        headers={"Cookie": f"token={auth_token}"},
        timeout=REQUEST_TIMEOUT,
    )
    assert delete.status_code == 201

    response = session.get(f"{BASE_URL}/booking/{created_booking['id']}", timeout=REQUEST_TIMEOUT)
    assert response.status_code == 404


@pytest.mark.parametrize("field, value", [("firstname", "Дмитрий"), ("firstname", "O'Brien-Smith")])
def test_names_accept_unicode_and_special_characters(session, auth_token, field, value):
    payload = build_booking(**{field: value})
    response = session.post(f"{BASE_URL}/booking", json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 200
    booking_id = response.json()["bookingid"]
    try:
        assert response.json()["booking"][field] == value
    finally:
        session.delete(
            f"{BASE_URL}/booking/{booking_id}",
            headers={"Cookie": f"token={auth_token}"},
            timeout=REQUEST_TIMEOUT,
        )
