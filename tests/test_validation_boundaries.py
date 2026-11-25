import pytest

from utilities.validation import validate_registration


def valid_data():
    return {
        "first_name": "A", "last_name": "B", "email": "valid@example.test",
        "mobile_number": "+1234567", "password": "Abcd123!",
        "confirm_password": "Abcd123!", "gender": "female",
        "date_of_birth": "2000-01-01", "address": "Somewhere",
        "country": "Country", "state": "State", "city": "City",
        "postal_code": "12345", "terms_accepted": True,
    }


@pytest.mark.parametrize("digits,valid", [(6, False), (7, True), (15, True), (16, False)])
def test_mobile_number_digit_boundaries(digits, valid):
    data = valid_data()
    data["mobile_number"] = "1" * digits
    assert ("mobile_number" not in validate_registration(data)) is valid


@pytest.mark.parametrize("length,valid", [(7, False), (8, True)])
def test_password_minimum_length_boundary(length, valid):
    data = valid_data()
    data["password"] = "A" + "b" * (length - 3) + "1!"
    data["confirm_password"] = data["password"]
    assert ("password" not in validate_registration(data)) is valid


@pytest.mark.parametrize("length,valid", [(80, True), (81, False)])
def test_first_name_maximum_length_boundary(length, valid):
    data = valid_data()
    data["first_name"] = "A" * length
    errors = validate_registration(data)
    assert ("first_name" not in errors) is valid


@pytest.mark.parametrize("first_name,last_name", [("O'Neil", "Smith"), ("Anne-Marie", "Lee")])
def test_names_with_common_special_characters_are_accepted(first_name, last_name):
    data = valid_data()
    data["first_name"] = first_name
    data["last_name"] = last_name
    assert validate_registration(data) == {}
