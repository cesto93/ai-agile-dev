import argparse
from config import load_config
from agent import create_stories


def list_stories():
    # Placeholder: Implement logic to list stories from storage
    print("Listing all user stories (not yet implemented).")


def main():
    parser = argparse.ArgumentParser(description="AI Agile Dev CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create user stories from documentation"
    )
    create_parser.add_argument(
        "--provider", required=True, help="Provider name (e.g., openai, azure)"
    )
    create_parser.add_argument(
        "--model", required=True, help="Model name (e.g., gpt-4, llama2)"
    )
    create_parser.add_argument(
        "--doc_path", required=True, help="Path to the documentation file"
    )
    create_parser.add_argument(
        "--minimal",
        action="store_true",
        help="Only extract minimal user story names without details",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all user stories")

    args = parser.parse_args()
    load_config()

    if args.command == "create":
        create_stories(args.provider, args.model, args.doc_path, args.minimal)
    elif args.command == "list":
        list_stories()


if __name__ == "__main__":
    main()
