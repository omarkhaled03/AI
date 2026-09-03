"""Schema-level validation tests for the Passenger request/response models.

These exercise app.models.passenger.PassengerCreate and PassengerListQuery
directly (no DB, no HTTP) since request validation lives in the Pydantic
schema layer per the architecture plan.
"""
from __future__ import annotations

import datetime

import pytest
from pydantic import ValidationError

from app.models.passenger import PassengerCreate, PassengerListQuery

VALID_PAYLOAD = {
    "full_name": "Jane Doe",
    "date_of_birth": "1990-01-15",
    "email": "Jane.Doe@Example.com",
    "phone": "+15551234567",
    "government_id_type": "passport",
    "government_id_number": "  ab1234567  ",
}


def _payload(**overrides):
    data = dict(VALID_PAYLOAD)
    data.update(overrides)
    return data


def test_create_valid_payload_succeeds():
    schema = PassengerCreate(**_payload())
    assert schema.full_name == "Jane Doe"


def test_create_missing_full_name_raises_validation_error():
    data = _payload()
    del data["full_name"]
    with pytest.raises(ValidationError):
        PassengerCreate(**data)


def test_create_missing_date_of_birth_raises_validation_error():
    data = _payload()
    del data["date_of_birth"]
    with pytest.raises(ValidationError):
        PassengerCreate(**data)


def test_create_missing_email_raises_validation_error():
    data = _payload()
    del data["email"]
    with pytest.raises(ValidationError):
        PassengerCreate(**data)


def test_create_missing_government_id_type_raises_validation_error():
    data = _payload()
    del data["government_id_type"]
    with pytest.raises(ValidationError):
        PassengerCreate(**data)


def test_create_missing_government_id_number_raises_validation_error():
    data = _payload()
    del data["government_id_number"]
    with pytest.raises(ValidationError):
        PassengerCreate(**data)


def test_create_without_phone_succeeds():
    data = _payload()
    del data["phone"]
    schema = PassengerCreate(**data)
    assert schema.phone is None


def test_create_future_date_of_birth_raises_validation_error():
    future = (
        datetime.datetime.now(tz=datetime.timezone.utc).date()
        + datetime.timedelta(days=1)
    ).isoformat()
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(date_of_birth=future))


def test_create_invalid_email_format_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(email="not-an-email"))


def test_create_empty_full_name_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(full_name=""))


def test_create_whitespace_only_full_name_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(full_name="   "))


def test_create_full_name_over_200_chars_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(full_name="A" * 201))


def test_create_government_id_number_over_50_chars_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(government_id_number="A" * 51))


def test_create_invalid_government_id_type_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerCreate(**_payload(government_id_type="drivers_license"))


def test_create_full_name_is_stored_trimmed():
    schema = PassengerCreate(**_payload(full_name="  Jane Doe  "))
    assert schema.full_name == "Jane Doe"


def test_create_email_is_stored_lowercased():
    schema = PassengerCreate(**_payload(email="Jane.Doe@Example.COM"))
    assert schema.email == "jane.doe@example.com"


def test_create_government_id_number_is_stored_trimmed_and_uppercased():
    schema = PassengerCreate(**_payload(government_id_number="  ab1234567  "))
    assert schema.government_id_number == "AB1234567"


def test_list_query_defaults_limit_20_offset_0():
    query = PassengerListQuery()
    assert query.limit == 20
    assert query.offset == 0


def test_list_query_limit_over_100_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerListQuery(limit=101)


def test_list_query_negative_offset_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerListQuery(offset=-1)


def test_list_query_zero_limit_raises_validation_error():
    with pytest.raises(ValidationError):
        PassengerListQuery(limit=0)
