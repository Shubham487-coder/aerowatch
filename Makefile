.PHONY: install lint format test check train up down deploy

install:
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest --cov

check: lint test

train up down deploy:
	@echo Not implemented yet
