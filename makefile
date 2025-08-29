coverage:
	uv run pytest --cov=src --cov-report=html tests/
venv:
	uv venv
format:
	ruff format
ui:
	uv run streamlit run src/ui.py
docker-build:
	docker build -t ai-agile-dev .
start:
	docker compose up -d
stop:
	docker compose down
requirements:
	uv pip compile pyproject.toml -o requirements.txt
