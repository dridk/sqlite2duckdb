
dev:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

build:
	rm -rf dist/ && uv build

publish:
	uv publish
