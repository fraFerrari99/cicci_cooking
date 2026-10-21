.DEFAULT_GOAL := help
.PHONY: help dev test lint fmt check up down logs pre-commit-install

help: ## Mostra questo aiuto
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Avvia l'API in locale con reload
	uv run uvicorn app.main:app --reload --port 8000

test: ## Esegue i test
	uv run pytest

lint: ## Ruff + mypy
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

fmt: ## Formatta e corregge ciò che ruff sa correggere
	uv run ruff check --fix .
	uv run ruff format .

check: lint test ## Tutto ciò che gira in CI

up: ## Avvia API + Postgres con Docker (con watch del codice)
	docker compose up --build --watch

down: ## Ferma i container
	docker compose down

logs: ## Log dei container
	docker compose logs -f

pre-commit-install: ## Installa i git hook (da eseguire una volta)
	uv run pre-commit install
