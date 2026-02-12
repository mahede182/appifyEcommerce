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
	pip install -r requirements.txt

dev:
	python manage.py runserver

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

shell:
	python manage.py shell

test:
	python manage.py test

lint:
	ruff check .

format:
	ruff format .

superuser:
	python manage.py createsuperuser

export:
	@echo "Dependencies already in requirements.txt"
	@echo "✓ Requirements file ready!"

schema:
	@mkdir -p schema
	python manage.py spectacular --color --file schema/openapi.yaml
	@echo "✓ OpenAPI schema generated at schema/openapi.yaml"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
