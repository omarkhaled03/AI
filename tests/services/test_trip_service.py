"""Service-layer tests for Trip creation and search.

Per docs/conventions.md, business logic is tested at the service layer
directly (against a real Postgres schema via db_session) rather than through
full HTTP round-trips. Trip has no uniqueness constraint (unlike Passenger),
so there is no conflict-error case here.
"""
from __future__ import annotations

import datetime

from app.models.trip import TripCreate, TripListQuery
from app.services.trip_service import create_trip, list_trips


def _create_payload(**overrides):
    data = {
        "destination": "Paris",
        "departure_date": "2026-06-10",
        "return_date": "2026-06-20",
    }
    data.update(overrides)
    return TripCreate(**data)


def test_create_trip_persists_and_returns_generated_id(db_session):
    trip = create_trip(db_session, _create_payload())
    assert trip.id is not None
    assert trip.destination == "Paris"


def test_create_trip_without_return_date_persists_with_null_return_date(db_session):
    payload = _create_payload()
    data = TripCreate(
        destination=payload.destination, departure_date=payload.departure_date
    )
    trip = create_trip(db_session, data)
    assert trip.return_date is None


def test_create_trip_with_departure_date_in_the_past_succeeds(db_session):
    trip = create_trip(
        db_session,
        TripCreate(destination="Cairo", departure_date="2020-01-01"),
    )
    assert trip.departure_date == datetime.date(2020, 1, 1)


def test_create_trip_allows_duplicate_destination_and_dates(db_session):
    first = create_trip(db_session, _create_payload())
    db_session.flush()
    second = create_trip(db_session, _create_payload())
    db_session.flush()

    assert first.id != second.id


def test_list_trips_returns_empty_list_when_none_exist(db_session):
    result = list_trips(db_session, TripListQuery())
    assert result.items == []
    assert result.total == 0


def test_list_trips_default_pagination_returns_created_at_desc(db_session):
    create_trip(db_session, _create_payload(destination="First"))
    db_session.flush()
    create_trip(db_session, _create_payload(destination="Second"))
    db_session.flush()

    result = list_trips(db_session, TripListQuery())
    destinations = [t.destination for t in result.items]
    assert destinations == ["Second", "First"]


def test_list_trips_respects_limit_and_offset(db_session):
    for i in range(3):
        create_trip(db_session, _create_payload(destination=f"City {i}"))
        db_session.flush()

    result = list_trips(db_session, TripListQuery(limit=1, offset=1))
    assert len(result.items) == 1
    assert result.total == 3


def test_list_trips_search_by_destination_case_insensitive_partial_match(db_session):
    create_trip(db_session, _create_payload(destination="Paris"))
    db_session.flush()
    create_trip(db_session, _create_payload(destination="London"))
    db_session.flush()

    result = list_trips(db_session, TripListQuery(destination="par"))
    assert len(result.items) == 1
    assert result.items[0].destination == "Paris"


def test_list_trips_search_by_destination_no_match_returns_empty(db_session):
    create_trip(db_session, _create_payload(destination="Paris"))
    db_session.flush()

    result = list_trips(db_session, TripListQuery(destination="Atlantis"))
    assert result.items == []
