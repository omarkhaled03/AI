"""Repository-layer tests for Trip persistence.

Trip has no uniqueness constraint (unlike Passenger), so these focus on
persistence of the nullable return_date column and on the
destination search/pagination behavior that only a real database can prove
(see docs/domain-rules.md's provenance note on Passenger vs. Trip identity).
"""
from __future__ import annotations

import datetime

from app.db.models import Trip
from app.repositories.trip_repository import TripRepository


def _make_trip(**overrides) -> Trip:
    defaults = {
        "destination": "Paris",
        "departure_date": datetime.date(2026, 6, 10),
        "return_date": datetime.date(2026, 6, 20),
    }
    defaults.update(overrides)
    return Trip(**defaults)


def test_add_persists_trip_and_generates_id(db_session):
    repo = TripRepository(db_session)
    trip = repo.add(_make_trip())
    db_session.flush()

    assert trip.id is not None


def test_add_persists_trip_without_return_date(db_session):
    repo = TripRepository(db_session)
    trip = repo.add(_make_trip(return_date=None))
    db_session.flush()

    assert trip.return_date is None


def test_search_by_destination_ilike_partial_case_insensitive(db_session):
    repo = TripRepository(db_session)
    repo.add(_make_trip(destination="Paris"))
    db_session.flush()
    repo.add(
        _make_trip(
            destination="London",
            departure_date=datetime.date(2026, 7, 1),
            return_date=None,
        )
    )
    db_session.flush()

    results, total = repo.search(destination="par", limit=20, offset=0)
    assert total == 1
    assert results[0].destination == "Paris"


def test_search_without_filters_returns_all_trips(db_session):
    repo = TripRepository(db_session)
    repo.add(_make_trip(destination="Paris"))
    db_session.flush()
    repo.add(
        _make_trip(
            destination="Rome",
            departure_date=datetime.date(2026, 8, 1),
            return_date=None,
        )
    )
    db_session.flush()

    results, total = repo.search(limit=20, offset=0)
    assert total == 2
    assert len(results) == 2


def test_search_pagination_respects_limit_and_offset(db_session):
    repo = TripRepository(db_session)
    for i in range(3):
        repo.add(
            _make_trip(
                destination=f"City {i}",
                departure_date=datetime.date(2026, 6, 10 + i),
            )
        )
        db_session.flush()

    results, total = repo.search(limit=2, offset=0)
    assert total == 3
    assert len(results) == 2


def test_search_with_no_matching_destination_returns_empty(db_session):
    repo = TripRepository(db_session)
    repo.add(_make_trip(destination="Paris"))
    db_session.flush()

    results, total = repo.search(destination="Atlantis", limit=20, offset=0)
    assert total == 0
    assert results == []
