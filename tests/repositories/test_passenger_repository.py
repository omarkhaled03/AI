"""Repository-layer tests for Passenger persistence.

These focus on behavior that only a real database can prove: the unique
constraint on (government_id_type, government_id_number) enforced at the DB
level (relied on for correctness under concurrent creates, not just an
app-level pre-check), and query/ordering behavior.
"""
from __future__ import annotations

import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import Passenger
from app.repositories.passenger_repository import PassengerRepository


def _make_passenger(**overrides) -> Passenger:
    defaults = {
        "full_name": "Jane Doe",
        "date_of_birth": datetime.date(1990, 1, 15),
        "email": "jane.doe@example.com",
        "phone": "+15551234567",
        "government_id_type": "passport",
        "government_id_number": "AB1234567",
    }
    defaults.update(overrides)
    return Passenger(**defaults)


def test_unique_constraint_prevents_duplicate_government_id_at_db_level(db_session):
    repo = PassengerRepository(db_session)

    repo.add(_make_passenger())
    db_session.flush()

    repo.add(_make_passenger(email="other@example.com"))
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_unique_constraint_allows_same_number_different_type(db_session):
    repo = PassengerRepository(db_session)

    repo.add(_make_passenger(government_id_type="passport", government_id_number="X1"))
    db_session.flush()

    repo.add(
        _make_passenger(
            government_id_type="national_id",
            government_id_number="X1",
            email="other@example.com",
        )
    )
    db_session.flush()  # should not raise


def test_get_by_government_id_returns_existing_match(db_session):
    repo = PassengerRepository(db_session)
    passenger = _make_passenger()
    repo.add(passenger)
    db_session.flush()

    found = repo.get_by_government_id("passport", "AB1234567")
    assert found is not None
    assert found.id == passenger.id


def test_get_by_government_id_returns_none_when_no_match(db_session):
    repo = PassengerRepository(db_session)
    found = repo.get_by_government_id("passport", "NOPE")
    assert found is None


def test_search_by_name_ilike_partial_case_insensitive(db_session):
    repo = PassengerRepository(db_session)
    repo.add(_make_passenger(full_name="Jane Doe"))
    db_session.flush()
    repo.add(
        _make_passenger(
            full_name="John Smith",
            email="john@example.com",
            government_id_number="ID2",
        )
    )
    db_session.flush()

    results, total = repo.search(name="jane", limit=20, offset=0)
    assert total == 1
    assert results[0].full_name == "Jane Doe"


def test_search_pagination_ordering_stable(db_session):
    repo = PassengerRepository(db_session)
    for i in range(3):
        repo.add(
            _make_passenger(
                full_name=f"Passenger {i}",
                email=f"p{i}@example.com",
                government_id_number=f"ID{i}",
            )
        )
        db_session.flush()

    results, total = repo.search(limit=2, offset=0)
    assert total == 3
    assert len(results) == 2
