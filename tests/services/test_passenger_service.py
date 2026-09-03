"""Service-layer tests for Passenger creation and search.

Per docs/conventions.md, business logic is tested at the service layer
directly (against a real Postgres schema via db_session) rather than through
full HTTP round-trips.
"""
from __future__ import annotations

import pytest

from app.models.passenger import PassengerCreate, PassengerListQuery
from app.services.passenger_service import (
    PassengerAlreadyExistsError,
    create_passenger,
    list_passengers,
)


def _create_payload(**overrides):
    data = {
        "full_name": "Jane Doe",
        "date_of_birth": "1990-01-15",
        "email": "jane.doe@example.com",
        "phone": "+15551234567",
        "government_id_type": "passport",
        "government_id_number": "AB1234567",
    }
    data.update(overrides)
    return PassengerCreate(**data)


def test_create_passenger_persists_and_returns_generated_id(db_session):
    passenger = create_passenger(db_session, _create_payload())
    assert passenger.id is not None
    assert passenger.full_name == "Jane Doe"


def test_create_passenger_duplicate_government_id_raises_conflict_error(db_session):
    first = create_passenger(db_session, _create_payload())
    db_session.flush()

    with pytest.raises(PassengerAlreadyExistsError) as exc_info:
        create_passenger(
            db_session,
            _create_payload(full_name="John Smith", email="john@example.com"),
        )

    assert exc_info.value.existing_passenger_id == first.id


def test_create_passenger_duplicate_is_detected_case_insensitively(db_session):
    first = create_passenger(
        db_session, _create_payload(government_id_number="ab1234567")
    )
    db_session.flush()

    with pytest.raises(PassengerAlreadyExistsError) as exc_info:
        create_passenger(
            db_session,
            _create_payload(
                government_id_number="  AB1234567  ",
                email="other@example.com",
            ),
        )

    assert exc_info.value.existing_passenger_id == first.id


def test_create_passenger_same_number_different_type_is_allowed(db_session):
    create_passenger(
        db_session,
        _create_payload(government_id_type="passport", government_id_number="X1"),
    )
    db_session.flush()

    passenger = create_passenger(
        db_session,
        _create_payload(
            government_id_type="national_id",
            government_id_number="X1",
            email="other@example.com",
        ),
    )
    assert passenger.id is not None


def test_list_passengers_returns_empty_list_when_none_exist(db_session):
    result = list_passengers(db_session, PassengerListQuery())
    assert result.items == []
    assert result.total == 0


def test_list_passengers_default_pagination_returns_created_at_desc(db_session):
    create_passenger(
        db_session,
        _create_payload(
            full_name="First", email="first@example.com", government_id_number="ID1"
        ),
    )
    db_session.flush()
    create_passenger(
        db_session,
        _create_payload(
            full_name="Second",
            email="second@example.com",
            government_id_number="ID2",
        ),
    )
    db_session.flush()

    result = list_passengers(db_session, PassengerListQuery())
    names = [p.full_name for p in result.items]
    assert names == ["Second", "First"]


def test_list_passengers_respects_limit_and_offset(db_session):
    for i in range(3):
        create_passenger(
            db_session,
            _create_payload(
                full_name=f"Passenger {i}",
                email=f"p{i}@example.com",
                government_id_number=f"ID{i}",
            ),
        )
        db_session.flush()

    result = list_passengers(db_session, PassengerListQuery(limit=1, offset=1))
    assert len(result.items) == 1
    assert result.total == 3


def test_list_passengers_search_by_government_id_number_exact_match(db_session):
    create_passenger(
        db_session,
        _create_payload(government_id_number="UNIQUE1", email="a@example.com"),
    )
    db_session.flush()
    create_passenger(
        db_session,
        _create_payload(government_id_number="UNIQUE2", email="b@example.com"),
    )
    db_session.flush()

    result = list_passengers(
        db_session, PassengerListQuery(government_id_number="unique1")
    )
    assert len(result.items) == 1
    assert result.items[0].government_id_number == "UNIQUE1"


def test_list_passengers_search_by_government_id_number_no_match_returns_empty(
    db_session,
):
    result = list_passengers(
        db_session, PassengerListQuery(government_id_number="NOPE")
    )
    assert result.items == []


def test_list_passengers_search_by_name_case_insensitive_partial_match(db_session):
    create_passenger(
        db_session, _create_payload(full_name="Jane Doe", email="jane@example.com")
    )
    db_session.flush()
    create_passenger(
        db_session,
        _create_payload(
            full_name="John Smith",
            email="john@example.com",
            government_id_number="ID2",
        ),
    )
    db_session.flush()

    result = list_passengers(db_session, PassengerListQuery(name="jane"))
    assert len(result.items) == 1
    assert result.items[0].full_name == "Jane Doe"
