#!/usr/bin/env bash
set -euo pipefail

# Fixed verification gate: no discovery, no subset selection.
# Stack: Python + FastAPI + PostgreSQL (see docs/architecture.md, docs/conventions.md)

echo "== typecheck =="
mypy app

echo "== lint =="
ruff check .

echo "== test =="
pytest

echo "verify.sh: all checks passed"
