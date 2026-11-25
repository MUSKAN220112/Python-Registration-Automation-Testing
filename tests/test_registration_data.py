from pathlib import Path

import pandas as pd
import pytest


DATA_DIR = Path(__file__).resolve().parents[1] / "test_data"
DATA_FILES = ("registration_data.csv", "registration_data.xlsx")
COLUMN_NAMES = {
    "TestCaseID": "test_case_id",
    "FirstName": "first_name",
    "LastName": "last_name",
    "Email": "email",
    "Mobile": "mobile_number",
    "Password": "password",
    "ConfirmPassword": "confirm_password",
    "Gender": "gender",
    "DateOfBirth": "date_of_birth",
    "Address": "address",
    "Country": "country",
    "State": "state",
    "City": "city",
    "PostalCode": "postal_code",
    "TermsAccepted": "terms_accepted",
    "Scenario": "scenario",
    "ExpectedResult": "source_expected_result",
}


def load_records(filename):
    path = DATA_DIR / filename
    if path.suffix.lower() == ".csv":
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    elif path.suffix.lower() == ".xlsx":
        frame = pd.read_excel(path, dtype=str, keep_default_na=False)
    else:
        raise ValueError(f"Unsupported test data file: {filename}")

    missing_columns = set(COLUMN_NAMES) - set(frame.columns)
    if missing_columns:
        raise ValueError(
            f"{filename} is missing required columns: {', '.join(sorted(missing_columns))}"
        )

    frame = frame.rename(columns=COLUMN_NAMES)
    records = frame.to_dict(orient="records")
    for record in records:
        record["terms_accepted"] = str(record["terms_accepted"]).strip().lower() in {
            "true", "yes", "1", "on",
        }
        is_duplicate = record["scenario"].strip().lower().startswith("duplicate email")
        source_result = record.pop("source_expected_result").strip().lower()
        if source_result not in {"success", "error"}:
            raise ValueError(
                f"{filename} has unsupported ExpectedResult for {record['test_case_id']}: "
                f"{source_result}"
            )
        record["is_duplicate"] = is_duplicate
        record["expected_result"] = (
            "duplicate" if is_duplicate else "success" if source_result == "success" else "invalid"
        )
        record["expected_status"] = (
            409 if is_duplicate else 201 if source_result == "success" else 400
        )
    return records


DATA_CASES = [
    pytest.param(filename, record, id=f"{filename}-{record['test_case_id']}")
    for filename in DATA_FILES
    for record in load_records(filename)
]


def registration_payload(record):
    return {key: record[key] for key in (
        "first_name", "last_name", "email", "mobile_number", "password",
        "confirm_password", "gender", "date_of_birth", "address", "country",
        "state", "city", "postal_code", "terms_accepted",
    )}


@pytest.mark.parametrize("filename,record", DATA_CASES)
def test_generated_registration_case(client, filename, record):
    payload = registration_payload(record)
    if record["is_duplicate"]:
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

    response = client.post("/api/register", json=payload)
    assert response.status_code == record["expected_status"], filename
    if record["expected_result"] == "success":
        assert response.get_json()["message"] == "Registration successful."
        assert response.get_json()["user_id"] > 0
    elif record["expected_result"] == "duplicate":
        assert "already exists" in response.get_json()["message"]
        assert "email" in response.get_json()["errors"]
    else:
        assert response.get_json()["errors"]
