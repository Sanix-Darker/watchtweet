PYTEST_CMD=TESTING=true pytest -n 4 tests -vv

SHELL := /bin/bash # Use bash syntax

# dev aliases format and lint
RUFF=ruff watchtweet tests
BLACK=black watchtweet tests
MYPY=mypy watchtweet tests

install: ## install poetry and pip + all deps for the project
	pip install -U pip poetry
	poetry install

format: ## Reformat project code.
	${RUFF} --fix
	${BLACK}

lint: ## Lint project code
	${RUFF}
	${BLACK} --check
	${MYPY}

test: ## to run tests
	${PYTEST_CMD}

docker-build: ## docker-build to build the bot watchtweet
	docker build -t watchtweet:latest -f Dockerfile .

run:
	python -m watchtweet.main

help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: install docker-build lint format test help
