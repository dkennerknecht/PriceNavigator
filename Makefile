SHELL := /bin/bash

.PHONY: backend-install frontend-install backend-dev frontend-dev db-upgrade seed test lint format docker-up

backend-install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

frontend-install:
	cd frontend && npm install

backend-dev:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	cd frontend && npm run dev

db-upgrade:
	cd backend && . .venv/bin/activate && alembic upgrade head

seed:
	cd backend && . .venv/bin/activate && python -m app.seed

test:
	cd backend && . .venv/bin/activate && pytest
	cd frontend && npm run test && npm run e2e

lint:
	cd backend && . .venv/bin/activate && ruff check .
	cd frontend && npm run lint

format:
	cd backend && . .venv/bin/activate && ruff format .
	cd frontend && npm run format

docker-up:
	docker compose up --build

