import time

import pytest
import requests


def valid_payload(email="api.test@example.test"):
    return {
        "first_name": "API", "last_name": "Tester", "email": email,
        "mobile_number": "+1 555 123 4567", "password": "StrongPass1!",
        "confirm_password": "StrongPass1!", "gender": "non-binary",
        "date_of_birth": "1992-04-20", "address": "5 API Avenue",
        "country": "Exampleland", "state": "State", "city": "City",
        "postal_code": "54321", "terms_accepted": True,
    }


@pytest.mark.api
def test_api_creates_user_and_returns_expected_response(api_base_url):
    start = time.perf_counter()
    response = requests.post(
        f"{api_base_url}/api/register",
        json=valid_payload(),
        timeout=5,
    )
    elapsed = time.perf_counter() - start
    assert response.status_code == 201
    assert response.json()["message"] == "Registration successful."
    assert isinstance(response.json()["user_id"], int)
    assert elapsed < 2.0
    assert "password" not in response.json()


@pytest.mark.api
@pytest.mark.parametrize("email", ["invalid", "user@", "@example.test", "user@example"])
def test_api_rejects_invalid_email(api_base_url, email):
    response = requests.post(
        f"{api_base_url}/api/register",
        json=valid_payload(email),
        timeout=5,
    )
    assert response.status_code == 400
    assert "email" in response.json()["errors"]


@pytest.mark.api
@pytest.mark.parametrize("field", ["first_name", "email", "mobile_number", "password", "terms_accepted"])
def test_api_rejects_missing_required_fields(api_base_url, field):
    payload = valid_payload(f"missing.{field}@example.test")
    payload.pop(field)
    response = requests.post(f"{api_base_url}/api/register", json=payload, timeout=5)
    assert response.status_code == 400
    assert field in response.json()["errors"]


@pytest.mark.api
def test_api_rejects_duplicate_registration(api_base_url):
    payload = valid_payload()
    first = requests.post(f"{api_base_url}/api/register", json=payload, timeout=5)
    second = requests.post(f"{api_base_url}/api/register", json=payload, timeout=5)
    assert first.status_code == 201
    assert second.status_code == 409
    assert "email" in second.json()["errors"]


@pytest.mark.api
@pytest.mark.parametrize("password", ["weakpass", "password1", "UPPERCASE1!", "lowercase!"])
def test_api_rejects_weak_passwords(api_base_url, password):
    payload = valid_payload(f"weak.{len(password)}@example.test")
    payload["password"] = password
    payload["confirm_password"] = password
    response = requests.post(f"{api_base_url}/api/register", json=payload, timeout=5)
    assert response.status_code == 400
    assert "password" in response.json()["errors"]


@pytest.mark.api
def test_api_rejects_non_json_body(api_base_url):
    response = requests.post(f"{api_base_url}/api/register", data="not json", timeout=5)
    assert response.status_code == 400
    assert "JSON object" in response.json()["message"]


@pytest.mark.api
def test_health_endpoint_returns_json(api_base_url):
    response = requests.get(f"{api_base_url}/health", timeout=5)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
