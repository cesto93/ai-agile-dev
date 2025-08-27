import argparse
from config import load_config
from agent import create_stories, list_stories, read_story


def main():
    parser = argparse.ArgumentParser(description="AI Agile Dev CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    create_parser = subparsers.add_parser(
        "create", help="Create user stories from documentation"
    )
    create_parser.add_argument(
        "--provider",
        required=True,
        help="Provider name (e.g., google_genai, ollama)",
        default="google_genai",
    )
    create_parser.add_argument(
        "--model",
        required=True,
        help="Model name (e.g., gemma3, gemini-2.5-flash)",
        default="gemini-2.5-flash",
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

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a user story by title")
    get_parser.add_argument("title", help="Title of the user story to retrieve")

    args = parser.parse_args()
    load_config()

    if args.command == "create":
        create_stories(args.provider, args.model, args.doc_path, args.minimal)
    elif args.command == "list":
        list_stories()
    elif args.command == "get":
        read_story(args.title)


if __name__ == "__main__":
    main()
