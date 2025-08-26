coverage:
	uv run pytest --cov=src --cov-report=html tests/
venv:
	uv venv
format:
	ruff format
