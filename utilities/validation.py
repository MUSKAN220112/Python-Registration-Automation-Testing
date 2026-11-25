import re
from datetime import date


EMAIL_PATTERN = re.compile(
    r"^[A-Z0-9_%+-]+(?:\.[A-Z0-9_%+-]+)*@"
    r"(?:[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?\.)+[A-Z]{2,}$",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s()-]{5,18}[0-9]$")
GENDERS = {"female", "male", "non-binary", "prefer-not-to-say"}


def validate_registration(data):
    errors = {}
    required = (
        "first_name", "last_name", "email", "mobile_number", "password",
        "confirm_password", "gender", "date_of_birth", "address", "country",
        "state", "city", "postal_code",
    )
    for field in required:
        if not str(data.get(field, "")).strip():
            errors[field] = "This field is required."

    for field in ("first_name", "last_name"):
        value = str(data.get(field, "")).strip()
        if value and len(value) > 80:
            errors[field] = "Must be 80 characters or fewer."

    email = str(data.get("email", "")).strip()
    if email and (len(email) > 254 or not EMAIL_PATTERN.fullmatch(email)):
        errors["email"] = "Enter a valid email address."

    password = str(data.get("password", ""))
    if password and (
        len(password) < 8
        or not re.search(r"[a-z]", password)
        or not re.search(r"[A-Z]", password)
        or not re.search(r"\d", password)
        or not re.search(r"[^A-Za-z0-9]", password)
    ):
        errors["password"] = (
            "Use at least 8 characters with uppercase, lowercase, a number, "
            "and a special character."
        )
    if data.get("confirm_password") and password != data.get("confirm_password"):
        errors["confirm_password"] = "Passwords do not match."

    phone = str(data.get("mobile_number", "")).strip()
    digits = re.sub(r"\D", "", phone)
    if phone and (not PHONE_PATTERN.fullmatch(phone) or not 7 <= len(digits) <= 15):
        errors["mobile_number"] = "Enter a valid mobile number (7 to 15 digits)."

    gender = str(data.get("gender", "")).strip().lower()
    if gender and gender not in GENDERS:
        errors["gender"] = "Select a valid gender option."

    dob = str(data.get("date_of_birth", "")).strip()
    if dob:
        try:
            date.fromisoformat(dob)
        except ValueError:
            errors["date_of_birth"] = "Enter a valid date of birth."

    if not data.get("terms_accepted"):
        errors["terms_accepted"] = "You must accept the terms and conditions."
    return errors
