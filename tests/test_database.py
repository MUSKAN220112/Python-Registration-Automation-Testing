import pytest
from werkzeug.security import check_password_hash

from database.db_utils import find_user_by_email
from tests.test_registration_data import registration_payload


def valid_payload(email="database.test@example.test"):
    return {
        "first_name": "Database", "last_name": "Tester", "email": email,
        "mobile_number": "+1 555 123 4567", "password": "SafePass1!",
        "confirm_password": "SafePass1!", "gender": "female",
        "date_of_birth": "1990-01-02", "address": "1 Database Road",
        "country": "Exampleland", "state": "State", "city": "City",
        "postal_code": "00001", "terms_accepted": True,
    }


@pytest.mark.database
def test_registration_persists_normalized_email_and_password_hash(app, client):
    payload = valid_payload("  Database.Test@Example.Test ")
    response = client.post("/api/register", json=payload)
    assert response.status_code == 201
    user = find_user_by_email(app.config["DATABASE_URL"], payload["email"])
    assert user is not None
    assert user.email == "database.test@example.test"
    assert user.password_hash != payload["password"]
    assert check_password_hash(user.password_hash, payload["password"])


@pytest.mark.database
def test_duplicate_registration_is_rejected(client):
    payload = valid_payload()
    assert client.post("/api/register", json=payload).status_code == 201
    response = client.post("/api/register", json=payload)
    assert response.status_code == 409
    assert response.get_json()["errors"]["email"]


@pytest.mark.database
def test_password_is_not_returned_by_api(client):
    response = client.post("/api/register", json=valid_payload())
    assert "password" not in response.get_json()
    assert "password_hash" not in response.get_json()
