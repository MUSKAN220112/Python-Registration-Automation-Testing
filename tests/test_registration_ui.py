import pytest

from pages.registration_page import RegistrationPage


def form_data(email="browser.test@example.test"):
    return {
        "first_name": "Browser", "last_name": "Tester", "email": email,
        "mobile_number": "+1 555 123 4567", "password": "StrongPass1!",
        "confirm_password": "StrongPass1!", "gender": "female",
        "date_of_birth": "1991-10-12", "address": "10 Browser Lane",
        "country": "Exampleland", "state": "State", "city": "City",
        "postal_code": "11111", "terms_accepted": True,
    }


@pytest.mark.ui
def test_ui_displays_registration_form(driver, live_app_url):
    page = RegistrationPage(driver, live_app_url).open()
    assert driver.title == "Create an account"
    assert driver.find_element("id", "email").is_displayed()


@pytest.mark.ui
def test_ui_accepts_valid_registration(driver, live_app_url):
    page = RegistrationPage(driver, live_app_url).open()
    page.fill(form_data()).submit()
    assert "Registration successful" in page.status_text()


@pytest.mark.ui
def test_ui_reports_invalid_email(driver, live_app_url):
    page = RegistrationPage(driver, live_app_url).open()
    page.fill(form_data("not-an-email"))
    assert driver.execute_script(
        "return arguments[0].validity.typeMismatch;",
        driver.find_element("id", "email"),
    )


@pytest.mark.ui
def test_ui_reports_password_mismatch(driver, live_app_url):
    data = form_data()
    data["confirm_password"] = "DifferentPass1!"
    page = RegistrationPage(driver, live_app_url).open()
    page.fill(data).submit()
    assert "do not match" in page.status_text().lower()


@pytest.mark.ui
def test_ui_reports_weak_password(driver, live_app_url):
    data = form_data()
    data["password"] = data["confirm_password"] = "weakpass"
    page = RegistrationPage(driver, live_app_url).open()
    page.fill(data).submit()
    assert "uppercase" in page.status_text().lower()


@pytest.mark.ui
def test_ui_reports_invalid_mobile(driver, live_app_url):
    data = form_data()
    data["mobile_number"] = "123"
    page = RegistrationPage(driver, live_app_url).open().fill(data)
    assert driver.execute_script(
        "return arguments[0].validity.patternMismatch;",
        driver.find_element("id", "mobile_number"),
    )


@pytest.mark.ui
def test_ui_reports_duplicate_email(driver, live_app_url):
    data = form_data()
    page = RegistrationPage(driver, live_app_url).open()
    page.fill(data).submit()
    assert "Registration successful" in page.status_text()
    page.open().fill(data).submit()
    assert "already exists" in page.status_text().lower()


@pytest.mark.ui
def test_ui_reset_button_clears_fields(driver, live_app_url):
    page = RegistrationPage(driver, live_app_url).open()
    page.fill(form_data()).reset()
    assert driver.find_element("id", "first_name").get_attribute("value") == ""
    assert not driver.find_element("name", "terms_accepted").is_selected()


@pytest.mark.ui
def test_ui_gender_dropdown_has_supported_values(driver, live_app_url):
    page = RegistrationPage(driver, live_app_url).open()
    values = [option.get_attribute("value") for option in
              driver.find_elements("css selector", "#gender option")]
    assert values == ["", "female", "male", "non-binary", "prefer-not-to-say"]


@pytest.mark.ui
def test_ui_terms_checkbox_is_required(driver, live_app_url):
    data = form_data()
    data["terms_accepted"] = False
    page = RegistrationPage(driver, live_app_url).open().fill(data)
    checkbox = driver.find_element("name", "terms_accepted")
    assert checkbox.get_attribute("required") is not None
    assert not checkbox.is_selected()


@pytest.mark.ui
def test_ui_browser_navigation_back_to_form(driver, live_app_url):
    page = RegistrationPage(driver, live_app_url).open()
    driver.get(live_app_url + "/health")
    assert '"status":"ok"' in driver.find_element("tag name", "body").text
    driver.back()
    assert driver.current_url == live_app_url + "/register"
    assert driver.find_element("id", "first_name").is_displayed()
