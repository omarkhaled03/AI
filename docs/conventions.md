# Conventions

## Structure

- `app/api/` — FastAPI routers (request/response handling only)
- `app/services/` — business logic
- `app/repositories/` — database access (SQLAlchemy)
- `app/models/` — Pydantic request/response schemas
- `app/db/models.py` — SQLAlchemy ORM models
- `tests/` — mirrors `app/` structure (e.g. `tests/services/test_reservation_service.py`)

## Testing

- Framework: `pytest`
- Test naming: `test_<behavior>_<condition>` (e.g. `test_reserve_fails_when_capacity_exhausted`)
- Prefer testing the service layer directly over full HTTP round-trips, except for a small number of API-level smoke tests per endpoint.
- Use an in-memory/test PostgreSQL schema per test run (not mocks) for repository-touching tests — this codebase's reservation-expiry correctness depends on real DB constraints (unique/check constraints), which mocks would hide.

## Style

- Type hints required on all function signatures.
- No bare `except:` — catch specific exceptions.
- Money/quantity fields are integers (cents / seat counts), never floats.

## Resource conventions (introduced with Passenger)

- Field normalization that participates in uniqueness checks or case-insensitive lookups (trim, case-fold) is done once, in the Pydantic schema layer (`app/models/`) via validators — not re-implemented in the service or repository layers.
- Duplicate-resource conflicts return `409` with body `{"detail": "<message>", "existing_<resource>_id": "<id>"}` (e.g. `existing_passenger_id`), so the caller can look up the conflicting row without a follow-up query. Generic error bodies otherwise are `{"detail": "<message>"}`.
- Uniqueness invariants that must hold under concurrent writes are enforced with a DB-level unique constraint (checked via `IntegrityError` in the service layer), not only an application-level pre-check query.
- List/search endpoints use `limit`/`offset` query params (default `limit=20`, max `100`); values above the max are rejected with `422`, never silently clamped.

## Resource conventions (introduced with Trip)

- Frontend 422 handling: when mapping a FastAPI validation-error array to form field errors by the last segment of `loc`, a cross-field/model-level validator (e.g. Pydantic `@model_validator(mode="after")`) produces `loc: ["body"]` with no field name — the last segment is the literal string `"body"`, not a real form field. Naively keying `fieldErrors` by that last segment (as `CreatePassengerPage` does, where every validator is field-level) silently drops the message. Any create-page 422 handler must check the resolved field name against the page's known form field names and route anything that doesn't match to the general form error instead of an unused field-error key.

_Update this file when a new convention is deliberately introduced — append, don't rewrite existing entries._
