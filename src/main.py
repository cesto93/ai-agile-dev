import argparse
from config import load_config
from genai import get_initial_state, get_stories_minimal


def main():
    parser = argparse.ArgumentParser(description="AI Agile Dev CLI")
    parser.add_argument(
        "--provider", required=True, help="Provider name (e.g., openai, azure)"
    )
    parser.add_argument(
        "--model", required=True, help="Model name (e.g., gpt-4, llama2)"
    )
    parser.add_argument(
        "--doc_path", required=True, help="Path to the documentation file"
    )
    args = parser.parse_args()

    load_config()
    state = get_initial_state(args.provider, args.model, args.doc_path)
    state = get_stories_minimal(state)


if __name__ == "__main__":
    main()
