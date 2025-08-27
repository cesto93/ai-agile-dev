import argparse
from config import load_config
from agent import create_stories


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
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Only extract minimal user story names without details",
    )
    args = parser.parse_args()

    load_config()
    create_stories(args.provider, args.model, args.doc_path, args.minimal)


if __name__ == "__main__":
    main()
