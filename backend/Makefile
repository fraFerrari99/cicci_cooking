.DEFAULT_GOAL := help
.PHONY: help dev test lint fmt check up down logs pre-commit-install

help: ## Show this help message with all the different commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start the API locally with reload
	uv run uvicorn app.main:app --reload --port 8000

test: ## Run the tests
	uv run pytest

lint: ## Ruff + mypy checks
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

fmt: ## Format and fix what ruff can correct
	uv run ruff check --fix .
	uv run ruff format .

check: lint test ## Everything that runs in CI

up: ## Start API + Postgres with Docker (with code watch)
	docker compose up --build --watch

down: ## Stop the containers
	docker compose down

logs: ## Logs of the containers
	docker compose logs -f

pre-commit-install: ## Install git hooks (to be run once)
	uv run pre-commit install
