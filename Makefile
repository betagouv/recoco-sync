#!make

SHELL := /bin/bash
TEST_ARGS ?=

runserver:
	@bash bin/run_server.sh dev

runworker:
	@bash bin/run_worker.sh

precommit:
	@pre-commit run --all-files

test:
	@pytest --maxfail=3 $(TEST_ARGS)

migrate:
	@python manage.py migrate

admin:
	@xdg-open http://localhost:8002/admin

install:
	@deactivate 2>/dev/null || true
	@rm -rf .venv
	@uv venv
	@source .venv/bin/activate
	@uv sync
