#!/usr/bin/env sh
set -eu

export DATABASE_URL="sqlite:///./data/e2e.sqlite"
export CORS_ORIGINS='["http://127.0.0.1:3100"]'
export PYTHONPATH="${PWD}"

. .venv/bin/activate
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 127.0.0.1 --port 8100
