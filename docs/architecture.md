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

## Design & color standard (Apple HIG-inspired)

All UI work follows Apple's [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) for color, type, and spacing. Tokens are defined once as CSS custom properties in `frontend/src/index.css` and consumed everywhere else — never hardcode a hex color in a component's CSS module.

- **System color palette** — Apple's system colors, used semantically rather than decoratively:
  - `--color-blue` `#007AFF` → `--color-primary` (primary actions, links, focus rings)
  - `--color-green` `#34C759` → `--color-success`
  - `--color-red` `#FF3B30` → `--color-danger`
  - `--color-orange` `#FF9500` → `--color-warning`
  - `--color-purple` `#AF52DE` → `--color-accent`
  - `--color-teal` `#30B0C7`, `--color-indigo` `#5856D6`, `--color-pink` `#FF2D55`, `--color-yellow` `#FFCC00` — available for secondary accents (badges, category tags, per-feature identity) so each resource's UI reads as visually distinct rather than one flat blue-on-white app.
  - Neutrals follow Apple's system gray scale (`--gray-1` darkest … `--gray-6` lightest) for surfaces, borders, and secondary text — never pure black/white.
- **Light/dark**: every color token has a light value in `:root` and a dark override under `@media (prefers-color-scheme: dark)`, so pages adapt automatically. Don't ship a component that only looks right in one mode.
- **Type**: `-apple-system, BlinkMacSystemFont, "SF Pro Text", ...` system font stack — no custom webfonts unless a requirement calls for brand typography.
- **Spacing**: 8pt grid (`--space-1` = 4px through `--space-5` = 32px). Pick from the scale rather than one-off pixel values.
- **Shape**: generous corner radii (`--radius-sm` 8px / `--radius-md` 12px / `--radius-lg` 18px, per Apple's rounded-rect language) and soft elevation (`--shadow-card`) instead of hard borders.
- **Color usage rule**: primary actions get a colored gradient/fill (primary → accent or primary → indigo); secondary/tertiary actions stay neutral. Status (success/error) always pairs a semantic color with a left-border accent and matching text color, not color alone. Use a distinct accent color per feature area's page header (e.g. teal for the Passengers list, matching its create-page's primary gradient) so users can tell pages apart at a glance — this is what keeps a growing multi-feature app feeling colorful and navigable rather than uniform gray-on-white.

## Reservation expiry mechanism

## Reservation expiry mechanism

Expired holds are not actively pushed anywhere — expiry is checked lazily: whenever remaining capacity for an event is computed, holds past their `expires_at` are treated as released (excluded from the count). A periodic cleanup job may later mark them released in storage, but correctness never depends on that job having run.

## Trip resource (TRV-6)

Second resource added after Passenger, following the same layering (`app/models/trip.py` -> `app/db/models.py::Trip` -> `app/repositories/trip_repository.py` -> `app/services/trip_service.py` -> `app/api/trips.py`, registered in `app/main.py`). Trip has no uniqueness constraint (no DB-level unique index, no `409` case, no `get_by_*` lookup on the repository) — unlike Passenger, whose identity key is `(government_id_type, government_id_number)`. Trip's migration is also the first in this repo generated with a real prior head (`down_revision` pointing at the Passenger migration, `3886e7e238a5`) rather than `down_revision = None`; generate it with `alembic revision --autogenerate -m "..."` against the current head instead of hand-rolling `down_revision`. TRV-8 (Booking) has a hard FK dependency on the `trips` table, so this migration must land and be applied before Booking's migration is written.

_Update this file when a requirement introduces a new component, service boundary, or significant tech choice._
