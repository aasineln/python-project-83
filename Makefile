PORT ?= 8000
APP_MODULE ?= 'page_analyzer:app'
FLASK_APP ?= run.py
PYTHON_VERSION ?= 3.12

.PHONY: install dev start render-start build lint lint-fix black

install:
	uv sync

dev:
	uv run flask --app $(APP_MODULE) --debug run --host=0.0.0.0 --port=$(PORT)

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) $(APP_MODULE)

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) $(APP_MODULE)

build:
	./build.sh

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

black:
	uv run black . --target-version py312 .
