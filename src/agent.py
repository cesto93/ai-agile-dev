from genai import get_initial_state, get_stories_minimal, refine_stories
from storage import get_story_by_title, save_story
from storage import get_story_titles


def create_stories(provider: str, model: str, problem_text: str, minimal: bool) -> None:
    state = get_initial_state(provider, model, problem_text)
    state = get_stories_minimal(state)
    if not minimal:
        state = refine_stories(state)
        for story in state["stories"]:
            save_story(story)


def read_story(title: str) -> None:
    content = get_story_by_title(title)
    print(content)
