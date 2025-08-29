from typing import TypedDict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from src.genai import (
    UserStory,
    UserStoryMinimal,
    clean_problem_description,
    get_stories_minimal,
    refine_stories,
)
from src.storage import save_story


class State(TypedDict):
    orig_problem_text: str
    problem_text: str
    stories_minimal: list[UserStoryMinimal]
    stories: list[UserStory]
    llm: BaseChatModel


def get_initial_state(provider: str, model: str, problem_text: str) -> State:
    """
    Returns the initial state for the agent.

    Args:
        provider (str): The provider for the language model.
        model (str): The model to use.
        problem_text (str): The text of the problem description.

    Returns:
        State: The initial state containing the document and llm.
    """
    llm = init_chat_model(f"{provider}:{model}")
    return {
        "orig_problem_text": problem_text,
        "problem_text": "",
        "stories_minimal": [],
        "stories": [],
        "llm": llm,
    }


def create_stories(provider: str, model: str, problem_text: str, minimal: bool) -> None:
    state = get_initial_state(provider, model, problem_text)
    state["problem_text"] = clean_problem_description(
        state["llm"], state["orig_problem_text"]
    )
    stories_minimal = get_stories_minimal(state["llm"], state["problem_text"])
    state["stories_minimal"] = stories_minimal
    if not minimal:
        stories = refine_stories(state["llm"], stories_minimal)
        state["stories"] = stories
        for story in stories:
            save_story(story)
