from genai import get_initial_state, get_stories_minimal, refine_stories
from storage import save_story


def create_stories(provider: str, model: str, problem_text: str, minimal: bool) -> None:
    state = get_initial_state(provider, model, problem_text)
    state = get_stories_minimal(state)
    if not minimal:
        state = refine_stories(state)
        for story in state["stories"]:
            save_story(story)
