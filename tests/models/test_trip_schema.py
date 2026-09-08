"""Schema-level validation tests for the Trip request/response models.

These exercise app.models.trip.TripCreate and TripListQuery directly (no DB,
no HTTP) since request validation lives in the Pydantic schema layer per the
architecture plan (mirrors tests/models/test_passenger_schema.py).
"""
from __future__ import annotations

import datetime

import pytest
from pydantic import ValidationError

from app.models.trip import TripCreate, TripListQuery

VALID_PAYLOAD = {
    "destination": "Paris",
    "departure_date": "2026-06-10",
    "return_date": "2026-06-20",
}


def _payload(**overrides):
    data = dict(VALID_PAYLOAD)
    data.update(overrides)
    return data


def test_create_valid_payload_succeeds():
    schema = TripCreate(**_payload())
    assert schema.destination == "Paris"


def test_create_missing_destination_raises_validation_error():
    data = _payload()
    del data["destination"]
    with pytest.raises(ValidationError):
        TripCreate(**data)


def test_create_missing_departure_date_raises_validation_error():
    data = _payload()
    del data["departure_date"]
    with pytest.raises(ValidationError):
        TripCreate(**data)


def test_create_without_return_date_succeeds():
    data = _payload()
    del data["return_date"]
    schema = TripCreate(**data)
    assert schema.return_date is None


def test_create_empty_destination_raises_validation_error():
    with pytest.raises(ValidationError):
        TripCreate(**_payload(destination=""))


def test_create_whitespace_only_destination_raises_validation_error():
    with pytest.raises(ValidationError):
        TripCreate(**_payload(destination="   "))


def test_create_destination_over_200_chars_raises_validation_error():
    with pytest.raises(ValidationError):
        TripCreate(**_payload(destination="A" * 201))


def test_create_destination_is_stored_trimmed():
    schema = TripCreate(**_payload(destination="  Paris  "))
    assert schema.destination == "Paris"


def test_create_departure_date_in_the_past_is_allowed():
    schema = TripCreate(**_payload(departure_date="2020-01-01", return_date=None))
    assert schema.departure_date == datetime.date(2020, 1, 1)


def test_create_departure_date_in_the_future_is_allowed():
    future = (
        datetime.datetime.now(tz=datetime.timezone.utc).date()
        + datetime.timedelta(days=365)
    ).isoformat()
    schema = TripCreate(**_payload(departure_date=future, return_date=None))
    assert schema.departure_date.isoformat() == future


def test_create_return_date_before_departure_date_raises_validation_error():
    with pytest.raises(ValidationError):
        TripCreate(
            **_payload(departure_date="2026-06-10", return_date="2026-06-01")
        )


def test_create_return_date_equal_to_departure_date_succeeds():
    schema = TripCreate(
        **_payload(departure_date="2026-06-10", return_date="2026-06-10")
    )
    assert schema.return_date == schema.departure_date


def test_create_return_date_after_departure_date_succeeds():
    schema = TripCreate(
        **_payload(departure_date="2026-06-10", return_date="2026-06-11")
    )
    assert schema.return_date > schema.departure_date


def test_list_query_defaults_limit_20_offset_0():
    query = TripListQuery()
    assert query.limit == 20
    assert query.offset == 0


def test_list_query_limit_over_100_raises_validation_error():
    with pytest.raises(ValidationError):
        TripListQuery(limit=101)


def test_list_query_negative_offset_raises_validation_error():
    with pytest.raises(ValidationError):
        TripListQuery(offset=-1)


def test_list_query_zero_limit_raises_validation_error():
    with pytest.raises(ValidationError):
        TripListQuery(limit=0)
