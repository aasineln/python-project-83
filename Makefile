.PHONY: install dev start build render-start test lint clean init-db

PORT ?= 8000

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

init-db:
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "DATABASE_URL is not set"; \
		exit 1; \
	fi
	psql -d $$DATABASE_URL -f database.sql

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

black:
	uv run black . --target-version py312 .
