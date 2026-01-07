.PHONY: all
all: lint test

.PHONY: lint
lint:
	uv run ruff check . --fix
	uv run ruff format .
	uv run ty check .

.PHONY: test
test:
	uv run pytest tests --cov
