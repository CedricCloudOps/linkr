.PHONY: help install lint test cov security run migrate image up down clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'

install: ## Create a virtualenv and install the package with dev extras
	python3 -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -e ".[dev]"

lint: ## Static analysis
	ruff check .

test: ## Unit tests
	pytest

cov: ## Tests with coverage report
	pytest --cov=linkr --cov-report=term-missing

security: ## SAST and dependency audit
	bandit -q -r src -c pyproject.toml
	pip-audit

run: ## Run the API locally (reload)
	uvicorn linkr.main:app --reload

migrate: ## Apply database migrations
	alembic upgrade head

image: ## Build the container image
	docker build -t linkr:local .

up: ## Start the full local stack
	docker compose up --build

down: ## Stop the local stack
	docker compose down -v

clean: ## Remove local build and cache artifacts
	rm -rf .venv .pytest_cache .ruff_cache coverage.xml *.db
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
