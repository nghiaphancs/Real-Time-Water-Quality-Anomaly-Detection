.PHONY: all setup test build run stop clean

PYTHON := .venv/bin/python
UVICORN := .venv/bin/uvicorn
PYTEST := .venv/bin/pytest

all: run

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	cd dashboard && npm install

test:
	$(PYTEST) tests/ -v

build-frontend:
	cd frontend && npm run build

run:
	./scripts/start.sh

stop:
	./scripts/stop.sh

status:
	./scripts/status.sh

clean:
	rm -rf data/runtime/*.db* data/runtime/*.pid logs/*.log logs/*.pid

