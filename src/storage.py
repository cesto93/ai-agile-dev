from typing import List, Any
import os
from tinydb import TinyDB, Query

DB_FILE = "stories_db.json"
STORIES_DIR = "stories"


class _Storage:
    """
    A singleton class to manage database and file storage for user stories.
    It centralizes database connection and path management.
    """

    def __init__(self) -> None:
        """
        Initializes the storage, setting up paths and the database connection.
        """
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(project_root, DB_FILE)
        self.stories_dir = os.path.join(project_root, STORIES_DIR)

        # Ensure stories directory exists
        os.makedirs(self.stories_dir, exist_ok=True)

        # Initialize TinyDB instance
        self.db = TinyDB(self.db_path)

    def save_story(self, story: Any) -> None:
        """
        Saves a user story as a markdown file and stores its metadata.

        Args:
            story (UserStory): The user story object.
        """
        # Save story as markdown file
        filename = f"{story.Title.replace(' ', '_')}.md"
        filepath = os.path.join(self.stories_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(story.to_template_string())

        # Save metadata to TinyDB
        self.db.insert({"title": story.Title, "file": filename})

    def save_problem_description(self, description: str) -> None:
        """
        Saves or updates the original problem description in the database.

        Args:
            description (str): The problem description text.
        """
        Problem = Query()
        self.db.upsert(
            {"type": "problem_description", "content": description},
            Problem.type == "problem_description",
        )

    def get_problem_description(self) -> str | None:
        """
        Retrieves the original problem description from the database.

        Returns:
            str or None: The problem description if found, else None.
        """
        Problem = Query()
        result = self.db.search(Problem.type == "problem_description")
        if result:
            return result[0]["content"]
        return None

    def get_story_titles(self) -> List[str]:
        """
        Returns a list of all story titles stored in the database.

        Returns:
            List[str]: List of story titles.
        """
        # Stories are identified by the presence of a 'title' field.
        # This implicitly filters out other document types like 'problem_description'.
        return [entry["title"] for entry in self.db.all() if "title" in entry]

    def get_story_by_title(self, title: str) -> str | None:
        """
        Retrieves a story by its title.

        Args:
            title (str): The title of the story.

        Returns:
            str or None: The story content if found, else None.
        """
        Story = Query()
        result = self.db.search(Story.title == title)
        if not result:
            return None
        filepath = os.path.join(self.stories_dir, result[0]["file"])
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                return content
        except FileNotFoundError:
            return None

    def remove_story_by_title(self, title: str) -> bool:
        """
        Removes a story by its title, deleting both the markdown file and the database entry.

        Args:
            title (str): The title of the story to remove.

        Returns:
            bool: True if the story was found and removed, False otherwise.
        """
        Story = Query()
        result = self.db.search(Story.title == title)
        if not result:
            return False

        # Remove the markdown file
        filepath = os.path.join(self.stories_dir, result[0]["file"])
        if os.path.exists(filepath):
            os.remove(filepath)

        # Remove the entry from the database
        self.db.remove(Story.title == title)
        return True

    def remove_all_story(self) -> None:
        """
        Removes all stories from markdown files and the database.
        This operation preserves other data types like the problem description.
        """
        Story = Query()
        stories_to_remove = self.db.search(Story.title.exists())

        # Remove all markdown files
        for story in stories_to_remove:
            filepath = os.path.join(self.stories_dir, story["file"])
            if os.path.exists(filepath):
                os.remove(filepath)

        # Remove all story entries from the database
        self.db.remove(Story.title.exists())

    def edit_story(self, title: str, new_content: str) -> bool:
        """
        Edits an existing story by its title, updating the markdown file content.

        Args:
            title (str): The title of the story to edit.
            new_content (str): The new content to write to the story file.

        Returns:
            bool: True if the story was found and edited, False otherwise.
        """
        Story = Query()
        result = self.db.search(Story.title == title)
        if not result:
            return False

        # Update the markdown file
        filepath = os.path.join(self.stories_dir, result[0]["file"])
        if os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        return False

    def rename_story(self, old_title: str, new_title: str) -> bool:
        """
        Renames an existing story by updating its title in the database and renaming the markdown file.

        Args:
            old_title (str): The current title of the story.
            new_title (str): The new title to assign to the story.

        Returns:
            bool: True if the story was found and renamed, False otherwise.
        """
        Story = Query()
        result = self.db.search(Story.title == old_title)
        if not result:
            return False

        # Rename the markdown file
        old_filepath = os.path.join(self.stories_dir, result[0]["file"])
        new_filename = f"{new_title.replace(' ', '_')}.md"
        new_filepath = os.path.join(self.stories_dir, new_filename)
        if os.path.exists(old_filepath):
            os.rename(old_filepath, new_filepath)

        # Update the entry in the database
        self.db.update(
            {"title": new_title, "file": new_filename}, Story.title == old_title
        )
        return True


# Singleton instance of the storage manager
_storage = _Storage()

# Expose the public methods of the singleton as module-level functions
# This maintains the existing API and avoids breaking changes in other modules.
save_story = _storage.save_story
save_problem_description = _storage.save_problem_description
get_problem_description = _storage.get_problem_description
get_story_titles = _storage.get_story_titles
get_story_by_title = _storage.get_story_by_title
remove_story_by_title = _storage.remove_story_by_title
remove_all_story = _storage.remove_all_story
edit_story = _storage.edit_story
rename_story = _storage.rename_story
