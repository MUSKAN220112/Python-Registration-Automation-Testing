from pathlib import Path

import pytest

from utilities import dashboard_data as dashboard_data_module


def registration_data(email="dashboard.user@example.test"):
    return {
        "first_name": "Dashboard",
        "last_name": "User",
        "email": email,
        "mobile_number": "+1234567",
        "password": "SecurePass1!",
        "confirm_password": "SecurePass1!",
        "gender": "female",
        "date_of_birth": "1995-06-15",
        "address": "1 Test Road",
        "country": "Exampleland",
        "state": "Test State",
        "city": "Test City",
        "postal_code": "12345",
        "terms_accepted": "on",
    }


def create_account(client, email="dashboard.user@example.test"):
    response = client.post("/register", data=registration_data(email))
    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert client.get("/login").status_code == 200


def test_root_opens_login_and_registration_remains_available(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to" in response.data
    assert b"Automation Testing" in response.data
    assert b"Total Test Executions" in response.data
    assert b"Automated testing" in response.data
    assert b"Forgot password?" in response.data
    assert b"Create an account" in client.get("/login").data
    assert b"Create an account" in client.get("/register").data


def test_landing_navigation_links_have_matching_sections(client):
    response = client.get("/")

    assert response.status_code == 200
    for section in (b"home", b"about", b"features", b"projects", b"test-reports", b"contact", b"login"):
        assert b'href="#' + section + b'"' in response.data
        assert b'id="' + section + b'"' in response.data


def test_login_remember_me_controls_persistent_session(client):
    create_account(client)

    response = client.post(
        "/login",
        data={"email": "dashboard.user@example.test", "password": "SecurePass1!"},
    )
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert not session.permanent

    client.post("/logout")
    client.post(
        "/login",
        data={
            "email": "dashboard.user@example.test",
            "password": "SecurePass1!",
            "remember_me": "on",
        },
    )
    with client.session_transaction() as session:
        assert session.permanent


def test_landing_execution_total_uses_valid_allure_results(tmp_path, monkeypatch):
    results_dir = tmp_path / "allure-results"
    results_dir.mkdir()
    (results_dir / "one-result.json").write_text(
        '{"name":"test_one","status":"passed","start":1760000000000,"stop":1760000000200}',
        encoding="utf-8",
    )
    (results_dir / "two-result.json").write_text(
        '{"name":"test_two","status":"failed","start":1760000001000,"stop":1760000001400}',
        encoding="utf-8",
    )
    (results_dir / "invalid-result.json").write_text("{invalid", encoding="utf-8")
    monkeypatch.setattr(dashboard_data_module, "REPORTS_DIR", tmp_path)

    dashboard = dashboard_data_module.get_dashboard_data()

    assert dashboard["total_executions"] == 2
    assert len(dashboard["recent_executions"]) == 2


def test_failed_login_does_not_open_dashboard(client):
    create_account(client)

    response = client.post(
        "/login",
        data={"email": "dashboard.user@example.test", "password": "incorrect"},
    )

    assert response.status_code == 401
    assert b"email address or password is incorrect" in response.data.lower()
    assert client.get("/dashboard").status_code == 302


def test_successful_login_redirects_to_dashboard(client):
    create_account(client)

    response = client.post(
        "/login",
        data={"email": "dashboard.user@example.test", "password": "SecurePass1!"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Welcome back, Dashboard" in response.data
    assert b"Total Projects" in response.data
    assert b"Total Test Cases" in response.data
    assert b"Passed Tests" in response.data
    assert b"Failed Tests" in response.data
    assert client.get("/").headers["Location"].endswith("/dashboard")


def test_dashboard_navigation_targets_exist(client):
    create_account(client)
    client.post(
        "/login",
        data={"email": "dashboard.user@example.test", "password": "SecurePass1!"},
    )
    response = client.get("/dashboard")

    assert response.status_code == 200
    for section in (b"dashboard", b"projects", b"test-cases", b"execution", b"reports", b"settings"):
        assert b'href="#' + section + b'"' in response.data
        assert b'id="' + section + b'"' in response.data


def test_logout_clears_dashboard_access(client):
    create_account(client)
    client.post(
        "/login",
        data={"email": "dashboard.user@example.test", "password": "SecurePass1!"},
    )

    response = client.post("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert client.get("/dashboard").status_code == 302


@pytest.mark.database
def test_html_report_requires_login_and_is_available_to_logged_in_user(client):
    report_path = Path(__file__).resolve().parents[1] / "reports" / "pytest-report.html"
    if not report_path.is_file():
        pytest.skip("No pytest HTML report is available.")

    denied = client.get("/reports/pytest-report.html")
    assert denied.status_code == 302

    create_account(client)
    client.post(
        "/login",
        data={"email": "dashboard.user@example.test", "password": "SecurePass1!"},
    )
    response = client.get("/reports/pytest-report.html")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    content_security_policy = response.headers["Content-Security-Policy"]
    assert "sandbox" in content_security_policy
    assert "allow-same-origin" in content_security_policy
