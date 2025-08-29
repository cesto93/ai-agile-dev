# ai-agile-dev

An utility to develop an agile software project using gen-ai.

Functionalities:
- Generate story from a requisite document
- View, Edit, Delete, Rename stories

Model providers supported:
 - google-genai
 - ollama

# Usage

## UI
uv run streamlit run src/ui.py

## Cli

Use google

uv run src/main.py create --provider google_genai --model gemini-2.5-flash --doc_path data/controllo_gruppi_consiliari.txt

Use ollama

uv run src/main.py create --provider ollama --model gemma3:270M --doc_path data/controllo_gruppi_consiliari.txt
