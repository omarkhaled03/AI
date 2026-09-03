# Architecture

## Stack

- **Backend language/framework**: Python, FastAPI
- **Frontend framework**: React (TypeScript)
- **Database**: PostgreSQL
- **API style**: REST, JSON request/response bodies

## Components

- **API layer** (`app/api/`) — FastAPI routers, one module per resource (e.g. `events`, `reservations`). Handles request validation (Pydantic models) and HTTP status codes; delegates business logic to the service layer.
- **Service layer** (`app/services/`) — business logic, including reservation holds/expiry. No direct SQL here; goes through the repository layer.
- **Repository layer** (`app/repositories/`) — database access (SQLAlchemy). One repository per aggregate (e.g. `EventRepository`, `ReservationRepository`).
- **Database** — PostgreSQL, migrations managed with Alembic.
- **Frontend** (`frontend/`) — React + TypeScript, built with Vite. One UI feature area per backend resource (e.g. `frontend/src/features/passengers/`), talking to the API layer over `fetch`/JSON — never directly to the database or service/repository layers.

## Frontend rules

- **Structure**: `frontend/src/features/<resource>/` per resource (e.g. `passengers`, `events`, `reservations`), each containing its page(s), components, and an `api.ts` for that resource's HTTP calls. Shared UI primitives (buttons, form fields, layout) live in `frontend/src/components/`; shared API plumbing (base fetch wrapper, error handling) lives in `frontend/src/lib/api.ts`.
- **State**: local component state (`useState`) by default; introduce a shared state library only if a requirement genuinely needs cross-page shared state — don't add one speculatively.
- **Styling**: plain CSS modules (`*.module.css`) co-located with components. No CSS-in-JS or utility-framework dependency unless a requirement calls for it.
- **API contract**: the frontend must consume the API exactly as the backend defines it (status codes, error body shape `{"detail": ...}` per `docs/conventions.md`) — do not add frontend-side workarounds for a backend inconsistency; fix the backend or flag it instead.
- **Every new backend resource/feature ships with a corresponding UI**: at minimum, a page to create a record (form matching the resource's required/optional fields and validation) and a page/view to list and search existing records, mirroring the resource's API endpoints. A feature is not complete until both the API and its UI exist.
- **Testing**: component/page tests with Vitest + React Testing Library, mirroring `frontend/src/` structure under `frontend/tests/`, following the same `test_<behavior>_<condition>`-style naming intent as the backend's pytest convention.

## Reservation expiry mechanism

## Reservation expiry mechanism

Expired holds are not actively pushed anywhere — expiry is checked lazily: whenever remaining capacity for an event is computed, holds past their `expires_at` are treated as released (excluded from the count). A periodic cleanup job may later mark them released in storage, but correctness never depends on that job having run.

_Update this file when a requirement introduces a new component, service boundary, or significant tech choice._
