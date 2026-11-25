import csv
from pathlib import Path

from openpyxl import Workbook


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "test_data"
FIELDS = [
    "first_name", "last_name", "email", "mobile_number", "password",
    "confirm_password", "gender", "date_of_birth", "address", "country",
    "state", "city", "postal_code", "terms_accepted", "expected_status",
    "expected_result", "is_duplicate",
]


def build_records():
    records = []

    def add(case_id, expected_status, expected_result, **changes):
        record = {
            "first_name": f"Test{case_id}", "last_name": "User",
            "email": f"qa.case{case_id}@example.test",
            "mobile_number": "+1 555 123 4567",
            "password": "StrongPass1!", "confirm_password": "StrongPass1!",
            "gender": "prefer-not-to-say", "date_of_birth": "1995-06-15",
            "address": "100 Test Street", "country": "Exampleland",
            "state": "Test State", "city": "Test City", "postal_code": "12345",
            "terms_accepted": True, "expected_status": expected_status,
            "expected_result": expected_result, "is_duplicate": False,
        }
        record.update(changes)
        records.append(record)

    for index in range(1, 11):
        add(f"valid{index}", 201, "success")

    invalid_emails = [
        "plainaddress", "@example.test", "qa@", "qa@.test", "qa..user@example.test",
        "qa user@example.test", "qa@example", "qa@example..test", ".qa@example.test",
        "qa@example.test.",
    ]
    for index, email in enumerate(invalid_emails, 11):
        add(f"email{index}", 400, "invalid", email=email)

    weak_passwords = ["short1!", "alllowercase1!", "ALLUPPERCASE1!", "NoDigits!!",
                      "NoSpecial123", "Aa1!", "password", "12345678", "AaAaAa1",
                      "weakpass!"]
    for index, password in enumerate(weak_passwords, 21):
        add(f"weak{index}", 400, "invalid", password=password, confirm_password=password)

    for index in range(31, 41):
        add(f"mismatch{index}", 400, "invalid", confirm_password="DifferentPass1!")

    invalid_phones = ["123", "abcdefgh", "123456", "+123456", "1234567890123456",
                      "++12345678", "123-ABC-7890", "(123", "123 456", "1" * 16]
    for index, phone in enumerate(invalid_phones, 41):
        add(f"phone{index}", 400, "invalid", mobile_number=phone)

    missing_fields = ["first_name", "last_name", "address", "postal_code", "date_of_birth"]
    for index, field in enumerate(missing_fields, 51):
        add(f"missing{index}", 400, "invalid", **{field: ""})

    for index in range(56, 61):
        add(f"terms{index}", 400, "invalid", terms_accepted=False)

    for index in range(61, 66):
        add(f"duplicate{index}", 409, "duplicate", is_duplicate=True)
    return records


def generate():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    records = build_records()
    csv_path = DATA_DIR / "registration_data.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow({**record, "terms_accepted": str(record["terms_accepted"]).lower(),
                             "is_duplicate": str(record["is_duplicate"]).lower()})

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Registration Data"
    sheet.append(FIELDS)
    for record in records:
        sheet.append([record[field] for field in FIELDS])
    workbook.save(DATA_DIR / "registration_data.xlsx")
    print(f"Generated {len(records)} test records in CSV and Excel.")


if __name__ == "__main__":
    generate()
