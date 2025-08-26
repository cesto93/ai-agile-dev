from typing import List
import os
from tinydb import TinyDB, Query

DB_FILE = "stories_db.json"
STORIES_DIR = "stories"


def save_story(story) -> None:
    """
    Saves a user story as a markdown file and stores its metadata.

    Args:
        story (UserStory): The user story object.
    """
    # Ensure stories directory exists
    stories_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    os.makedirs(stories_dir, exist_ok=True)

    # Save story as markdown file
    filename = f"{story.Title.replace(' ', '_')}.md"
    filepath = os.path.join(stories_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(story.to_template_string())

    # Save metadata to TinyDB
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    db.insert({"title": story.Title, "file": filename})
