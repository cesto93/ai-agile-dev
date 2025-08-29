import typer
import logging
from config import load_config
from agent import create_stories
from storage import (
    get_story_by_title,
    get_story_titles,
    remove_story_by_title,
    remove_all_story,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")

app = typer.Typer(
    help="AI Agile Dev CLI",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def create(
    provider: str = typer.Option(
        "google_genai", help="Provider name (e.g., google_genai, ollama)"
    ),
    model: str = typer.Option(
        "gemini-2.5-flash-lite", help="Model name (e.g., gemma3, gemini-2.5-flash)"
    ),
    doc_path: str = typer.Option(..., help="Path to the documentation file"),
    minimal: bool = typer.Option(
        False, help="Only extract minimal user story names without details"
    ),
):
    """Create user stories from documentation."""
    load_config()
    with open(doc_path, "r", encoding="utf-8") as f:
        problem_text = f.read()
    create_stories(provider, model, problem_text, minimal)


@app.command()
def list():
    """List all user stories."""
    load_config()
    stories = get_story_titles()
    for title in stories:
        logging.info(title)


@app.command()
def get(title: str = typer.Argument(..., help="Title of the user story to retrieve")):
    """Get a user story by title."""
    load_config()
    content = get_story_by_title(title)
    logging.info(content)


@app.command()
def rm(
    title: str = typer.Argument(
        None,
        help="Title of the user story to remove (omit to remove all stories)",
    ),
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Remove all user stories",
    ),
):
    """Remove a user story by title or all stories."""
    load_config()
    if all:
        remove_all_story()
        logging.info("All stories removed.")
    elif title:
        removed = remove_story_by_title(title)
        if removed:
            logging.info(f"Story '{title}' removed.")
        else:
            logging.info(f"Story '{title}' not found.")
    else:
        logging.info("Please provide a title or use --all to remove all stories.")


if __name__ == "__main__":
    app()
