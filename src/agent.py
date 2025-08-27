from genai import get_initial_state, get_stories_minimal, refine_stories
from storage import save_story


def create_stories(provider: str, model: str, doc_path: str, minimal: bool) -> None:
    state = get_initial_state(provider, model, doc_path)
    state = get_stories_minimal(state)
    if not minimal:
        state = refine_stories(state)
        for story in state["stories"]:
            save_story(story)
