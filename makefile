.PHONY: help install dev migrate makemigrations shell test lint format clean superuser export schema

help:
	@echo "Available commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make dev            - Run development server"
	@echo "  make migrate        - Run migrations"
	@echo "  make makemigrations - Create migrations"
	@echo "  make shell          - Open Django shell"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linting"
	@echo "  make format         - Format code"
	@echo "  make superuser      - Create superuser"
	@echo "  make export         - Export dependencies to requirements/"
	@echo "  make schema         - Generate OpenAPI schema"
	@echo "  make clean          - Clean cache files"

install:
	uv sync --locked

dev:
	uv run python manage.py runserver

migrate:
	uv run python manage.py migrate

makemigrations:
	uv run python manage.py makemigrations

shell:
	uv run python manage.py shell

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

superuser:
	uv run python manage.py createsuperuser

export:
	@echo "Exporting dependencies to requirements/..."
	uv export --no-hashes --no-dev > requirements/base.txt
	uv export --no-hashes > requirements/local.txt
	echo "-r base.txt" > requirements/production.txt
	@echo "✓ Dependencies exported successfully!"

schema:
	@mkdir -p schema
	uv run python manage.py spectacular --color --file schema/openapi.yaml
	@echo "✓ OpenAPI schema generated at schema/openapi.yaml"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
