PORT ?= 8000
APP_MODULE ?= wsgi:app
FLASK_APP ?= run.py
PYTHON_VERSION ?= 3.12

install:
	uv sync

dev:
	uv run flask --debug --app run

.PHONY: start
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) $(APP_MODULE)

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

black:
	uv run black . --target-version py312 .
