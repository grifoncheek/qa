import pytest

from conftest import BASE_URL, REQUEST_TIMEOUT, build_booking

pytestmark = pytest.mark.integration



@pytest.mark.xfail(reason="BUG-01: 500 вместо 400 при отсутствии firstname", strict=False)
def test_create_without_required_field_returns_400(session):
    payload = build_booking()
    payload.pop("firstname")

    response = session.post(f"{BASE_URL}/booking", json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-02: 500 при null в обязательном поле", strict=False)
def test_create_with_null_firstname_returns_400(session):
    response = session.post(f"{BASE_URL}/booking", json=build_booking(firstname=None), timeout=REQUEST_TIMEOUT)

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-03: 500 при строке вместо объекта bookingdates", strict=False)
def test_create_with_invalid_dates_type_returns_400(session):
    payload = build_booking()
    payload["bookingdates"] = "2026-12-10"

    response = session.post(f"{BASE_URL}/booking", json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-06: totalprice строкой принимается, значение теряется", strict=False)
def test_create_with_string_totalprice_returns_400(session):
    response = session.post(
        f"{BASE_URL}/booking", json=build_booking(totalprice="1234"), timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-07: отрицательный totalprice принимается", strict=False)
def test_create_with_negative_totalprice_returns_400(session):
    response = session.post(
        f"{BASE_URL}/booking", json=build_booking(totalprice=-100), timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-08: checkout раньше checkin принимается", strict=False)
def test_create_with_checkout_before_checkin_returns_400(session):
    payload = build_booking(bookingdates={"checkin": "2026-05-01", "checkout": "2026-01-02"})

    response = session.post(f"{BASE_URL}/booking", json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-13: несуществующая дата принимается и искажается", strict=False)
def test_create_with_invalid_date_value_returns_400(session):
    payload = build_booking(bookingdates={"checkin": "2026-13-45", "checkout": "2026-13-50"})

    response = session.post(f"{BASE_URL}/booking", json=payload, timeout=REQUEST_TIMEOUT)

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-14: null в totalprice приводит к 500", strict=False)
def test_create_with_null_totalprice_returns_400(session):
    response = session.post(
        f"{BASE_URL}/booking", json=build_booking(totalprice=None), timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400


@pytest.mark.xfail(reason="BUG-04: 500 вместо 415 при неподдерживаемом Content-Type", strict=False)
def test_create_with_unsupported_content_type_returns_415(session):
    payload = build_booking()

    response = session.post(
        f"{BASE_URL}/booking",
        data=str(payload).replace("'", '"'),
        headers={"Content-Type": "text/plain"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 415


@pytest.mark.xfail(reason="BUG-05: 500 вместо 400 при невалидной дате в фильтре", strict=False)
def test_filter_with_invalid_date_returns_400(session):
    response = session.get(
        f"{BASE_URL}/booking", params={"checkin": "not-a-date"}, timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 400


def test_create_with_malformed_json_returns_400(session):
    response = session.post(
        f"{BASE_URL}/booking",
        data="{oops",
        headers={"Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )

    assert response.status_code == 400


def test_update_without_token_returns_403(session):
    response = session.put(
        f"{BASE_URL}/booking/1", json=build_booking(), timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == 403


def test_get_nonexistent_booking_returns_404(session):
    response = session.get(f"{BASE_URL}/booking/999999999", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 404


def test_get_booking_with_non_numeric_id_returns_404(session):
    response = session.get(f"{BASE_URL}/booking/abc", timeout=REQUEST_TIMEOUT)

    assert response.status_code == 404
