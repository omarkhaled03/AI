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
- Cross-field validation (e.g. one date field must not precede another) is done with a Pydantic v2 `@model_validator(mode="after")` on the request schema, alongside `@field_validator` for single-field normalization — both live in `app/models/`, not in the service/repository layers (introduced with Trip's `return_date >= departure_date` check).
- Not every resource needs a uniqueness invariant or `409` case: a resource with no natural key (e.g. Trip) has no `get_by_*` lookup on its repository and no `IntegrityError` handling in its service — don't add either speculatively.

_Update this file when a new convention is deliberately introduced — append, don't rewrite existing entries._
