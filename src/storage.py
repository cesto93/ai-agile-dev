from typing import List
import os
from tinydb import TinyDB, Query

DB_FILE = "stories_db.json"
STORIES_DIR = "stories"


def save_note(note: str, title: str, text: str) -> None:
    """
    Saves a note with the given content, argument, and tags.

    Args:
        note (str): The content of the note.
        title (str): The note title.
        tags (List[str]): A list of tags associated with the note.
    """
    # Ensure notes directory exists
    notes_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    os.makedirs(notes_dir, exist_ok=True)

    # Save note as markdown file
    filename = f"{title.replace(' ', '_')}.md"
    filepath = os.path.join(notes_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note)

    # Save metadata to TinyDB
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    db.insert({"title": title})
