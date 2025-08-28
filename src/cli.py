import typer
from config import load_config
from agent import create_stories, list_stories, read_story

app = typer.Typer(help="AI Agile Dev CLI")


@app.command()
def create(
    provider: str = typer.Option(
        "google_genai", help="Provider name (e.g., google_genai, ollama)"
    ),
    model: str = typer.Option(
        "gemini-2.5-flash", help="Model name (e.g., gemma3, gemini-2.5-flash)"
    ),
    doc_path: str = typer.Option(..., help="Path to the documentation file"),
    minimal: bool = typer.Option(
        False, help="Only extract minimal user story names without details"
    ),
):
    """Create user stories from documentation."""
    load_config()
    create_stories(provider, model, doc_path, minimal)


@app.command()
def list():
    """List all user stories."""
    load_config()
    list_stories()


@app.command()
def get(title: str = typer.Argument(..., help="Title of the user story to retrieve")):
    """Get a user story by title."""
    load_config()
    read_story(title)


if __name__ == "__main__":
    app()
