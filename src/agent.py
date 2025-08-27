from genai import get_initial_state, get_stories_minimal, refine_stories
from storage import get_story_by_title, save_story
from storage import get_story_titles


def create_stories(provider: str, model: str, doc_path: str, minimal: bool) -> None:
    state = get_initial_state(provider, model, doc_path)
    state = get_stories_minimal(state)
    if not minimal:
        state = refine_stories(state)
        for story in state["stories"]:
            save_story(story)


def list_stories() -> None:
    stories = get_story_titles()
    for title in stories:
        print(title)


def read_story(title: str) -> None:
    content = get_story_by_title(title)
    print(content)
