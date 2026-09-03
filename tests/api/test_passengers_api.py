"""API-level smoke tests for the /passengers endpoints.

Per docs/conventions.md, the bulk of behavior is covered at the service
layer (see tests/services/test_passenger_service.py and
tests/repositories/test_passenger_repository.py); this file only checks
that the HTTP layer wires status codes and response shapes correctly.
"""
from __future__ import annotations

VALID_PAYLOAD = {
    "full_name": "Jane Doe",
    "date_of_birth": "1990-01-15",
    "email": "jane.doe@example.com",
    "phone": "+15551234567",
    "government_id_type": "passport",
    "government_id_number": "AB1234567",
}


def test_post_passengers_valid_request_returns_201_with_id(client):
    response = client.post("/passengers", json=VALID_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["full_name"] == "Jane Doe"


def test_post_passengers_missing_required_field_returns_422(client):
    payload = dict(VALID_PAYLOAD)
    del payload["email"]
    response = client.post("/passengers", json=payload)
    assert response.status_code == 422


def test_post_passengers_duplicate_government_id_returns_409_with_existing_id(client):
    first = client.post("/passengers", json=VALID_PAYLOAD)
    assert first.status_code == 201
    existing_id = first.json()["id"]

    duplicate_payload = dict(VALID_PAYLOAD)
    duplicate_payload["email"] = "someone-else@example.com"
    response = client.post("/passengers", json=duplicate_payload)

    assert response.status_code == 409
    body = response.json()
    assert body["existing_passenger_id"] == existing_id
    assert "detail" in body


def test_get_passengers_returns_200_empty_list_when_none_exist(client):
    response = client.get("/passengers")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []


def test_get_passengers_returns_200_with_created_passengers(client):
    client.post("/passengers", json=VALID_PAYLOAD)

    response = client.get("/passengers")
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["full_name"] == "Jane Doe"


def test_get_passengers_over_max_limit_returns_422(client):
    response = client.get("/passengers", params={"limit": 101})
    assert response.status_code == 422


def test_get_passengers_search_by_name_case_insensitive_partial_match(client):
    client.post("/passengers", json=VALID_PAYLOAD)
    other_payload = dict(VALID_PAYLOAD)
    other_payload.update(
        {
            "full_name": "John Smith",
            "email": "john@example.com",
            "government_id_number": "ZZ999",
        }
    )
    client.post("/passengers", json=other_payload)

    response = client.get("/passengers", params={"name": "jane"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["full_name"] == "Jane Doe"
