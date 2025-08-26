from typing import List
import os
from tinydb import TinyDB, Query

DB_FILE = "notes_db.json"
NOTES_DIR = "notes"


def save_note(note: str, title: str, tags: List[str]) -> None:
    """
    Saves a note with the given content, argument, and tags.

    Args:
        note (str): The content of the note.
        title (str): The note title.
        tags (List[str]): A list of tags associated with the note.
    """
    # Ensure notes directory exists
    notes_dir = os.path.join(os.path.dirname(__file__), "..", NOTES_DIR)
    os.makedirs(notes_dir, exist_ok=True)

    # Save note as markdown file
    filename = f"{title.replace(' ', '_')}.md"
    filepath = os.path.join(notes_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note)

    # Save metadata to TinyDB
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    db.insert({"argument": title, "tags": tags})
