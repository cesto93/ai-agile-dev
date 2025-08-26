# ai-agile-dev

An utility to develop an agile software project

# Usage

Use google

uv run src/main.py --provider google_genai --model gemini-2.5-flash --doc_path data/controllo_gruppi_consiliari.txt

Use ollama

uv run src/main.py --provider ollama --model gemma3:270M --doc_path data/controllo_gruppi_consiliari.txt
