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


def save_problem_description(description: str) -> None:
    """
    Saves or updates the original problem description in the database.

    Args:
        description (str): The problem description text.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    Problem = Query()
    db.upsert(
        {"type": "problem_description", "content": description},
        Problem.type == "problem_description",
    )


def get_problem_description() -> str | None:
    """
    Retrieves the original problem description from the database.

    Returns:
        str or None: The problem description if found, else None.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    Problem = Query()
    result = db.search(Problem.type == "problem_description")
    if result:
        return result[0]["content"]
    return None


def get_story_titles() -> List[str]:
    """
    Returns a list of all story titles stored in the database.

    Returns:
        List[str]: List of story titles.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    return [entry["title"] for entry in db.all() if "title" in entry]


def get_story_by_title(title: str) -> str | None:
    """
    Retrieves a story by its title.

    Args:
        title (str): The title of the story.

    Returns:
        str or None: The story content if found, else None.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    Story = Query()
    result = db.search(Story.title == title)
    if not result:
        return None
    stories_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    filepath = os.path.join(stories_dir, result[0]["file"])
    with open(filepath, "r") as f:
        content = f.read()
        return content


def remove_story_by_title(title: str) -> bool:
    """
    Removes a story by its title, deleting both the markdown file and the database entry.

    Args:
        title (str): The title of the story to remove.

    Returns:
        bool: True if the story was found and removed, False otherwise.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    Story = Query()
    result = db.search(Story.title == title)
    if not result:
        return False

    # Remove the markdown file
    stories_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    filepath = os.path.join(stories_dir, result[0]["file"])
    if os.path.exists(filepath):
        os.remove(filepath)

    # Remove the entry from the database
    db.remove(Story.title == title)
    return True


def remove_all_story() -> None:
    """
    Removes all stories from the markdown files and clears the database.
    """
    # Remove all markdown files in the stories directory
    stories_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    if os.path.exists(stories_dir):
        for filename in os.listdir(stories_dir):
            file_path = os.path.join(stories_dir, filename)
            if os.path.isfile(file_path) and filename.endswith(".md"):
                os.remove(file_path)

    # Clear the database
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    db.truncate()


def edit_story(title: str, new_content: str) -> bool:
    """
    Edits an existing story by its title, updating the markdown file content.

    Args:
        title (str): The title of the story to edit.
        new_content (str): The new content to write to the story file.

    Returns:
        bool: True if the story was found and edited, False otherwise.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    Story = Query()
    result = db.search(Story.title == title)
    if not result:
        return False

    # Update the markdown file
    stories_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    filepath = os.path.join(stories_dir, result[0]["file"])
    if os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def rename_story(old_title: str, new_title: str) -> bool:
    """
    Renames an existing story by updating its title in the database and renaming the markdown file.

    Args:
        old_title (str): The current title of the story.
        new_title (str): The new title to assign to the story.

    Returns:
        bool: True if the story was found and renamed, False otherwise.
    """
    db_path = os.path.join(os.path.dirname(__file__), "..", DB_FILE)
    db = TinyDB(db_path)
    Story = Query()
    result = db.search(Story.title == old_title)
    if not result:
        return False

    # Rename the markdown file
    stories_dir = os.path.join(os.path.dirname(__file__), "..", STORIES_DIR)
    old_filepath = os.path.join(stories_dir, result[0]["file"])
    new_filename = f"{new_title.replace(' ', '_')}.md"
    new_filepath = os.path.join(stories_dir, new_filename)
    if os.path.exists(old_filepath):
        os.rename(old_filepath, new_filepath)

    # Update the entry in the database
    db.update({"title": new_title, "file": new_filename}, Story.title == old_title)
    return True
