# abcd

FastAPI + PostgreSQL backend with a React (Vite) frontend.

## Prerequisites

- Python 3.10+
- PostgreSQL running locally
- Node.js (for the frontend)

## Backend setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Set the database URL (defaults to `postgresql+psycopg://localhost/abcd` if unset):

```bash
export DATABASE_URL=postgresql+psycopg://localhost/abcd
```

Create the database, then run migrations:

```bash
createdb abcd
alembic upgrade head
```

Run the API:

```bash
uvicorn app.main:app --reload
```

The API listens on `http://localhost:8000`.

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local   # sets VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

The frontend runs on `http://localhost:5173` (allowed by the backend's CORS config via `CORS_ALLOWED_ORIGINS`).

## Database migrations

Migrations live in [migrations/](migrations/) and are managed with Alembic.

```bash
alembic upgrade head                        # apply all migrations
alembic revision --autogenerate -m "..."    # create a new migration
alembic downgrade -1                        # roll back one migration
```

## Tests & checks

Backend:

```bash
pytest
```

Frontend:

```bash
cd frontend && npm test
```

Full verification gate (typecheck, lint, tests):

```bash
scripts/verify.sh
```

## Docs

- [docs/architecture.md](docs/architecture.md)
- [docs/conventions.md](docs/conventions.md)
- [docs/domain-rules.md](docs/domain-rules.md)
