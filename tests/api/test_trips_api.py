"""API-level smoke tests for the /trips endpoints.

Per docs/conventions.md, the bulk of behavior is covered at the service
layer (see tests/services/test_trip_service.py and
tests/repositories/test_trip_repository.py); this file only checks that the
HTTP layer wires status codes and response shapes correctly.
"""
from __future__ import annotations

VALID_PAYLOAD = {
    "destination": "Paris",
    "departure_date": "2026-06-10",
    "return_date": "2026-06-20",
}


def test_post_trips_valid_request_returns_201_with_id(client):
    response = client.post("/trips", json=VALID_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["destination"] == "Paris"
    assert body["departure_date"] == "2026-06-10"
    assert body["return_date"] == "2026-06-20"
    assert "created_at" in body


def test_post_trips_missing_destination_returns_422(client):
    payload = dict(VALID_PAYLOAD)
    del payload["destination"]
    response = client.post("/trips", json=payload)
    assert response.status_code == 422


def test_post_trips_missing_departure_date_returns_422(client):
    payload = dict(VALID_PAYLOAD)
    del payload["departure_date"]
    response = client.post("/trips", json=payload)
    assert response.status_code == 422


def test_post_trips_without_return_date_returns_201_with_null_return_date(client):
    payload = dict(VALID_PAYLOAD)
    del payload["return_date"]
    response = client.post("/trips", json=payload)
    assert response.status_code == 201
    assert response.json()["return_date"] is None


def test_post_trips_return_date_before_departure_date_returns_422(client):
    payload = dict(VALID_PAYLOAD)
    payload["return_date"] = "2026-06-01"
    response = client.post("/trips", json=payload)
    assert response.status_code == 422


def test_get_trips_returns_200_empty_list_when_none_exist(client):
    response = client.get("/trips")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["offset"] == 0


def test_get_trips_returns_200_with_created_trips(client):
    client.post("/trips", json=VALID_PAYLOAD)

    response = client.get("/trips")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["destination"] == "Paris"


def test_get_trips_over_max_limit_returns_422(client):
    response = client.get("/trips", params={"limit": 101})
    assert response.status_code == 422


def test_get_trips_search_by_destination_case_insensitive_partial_match(client):
    client.post("/trips", json=VALID_PAYLOAD)
    other_payload = dict(VALID_PAYLOAD)
    other_payload["destination"] = "London"
    client.post("/trips", json=other_payload)

    response = client.get("/trips", params={"destination": "par"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["destination"] == "Paris"
