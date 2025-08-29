import logging
from typing import TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from storage import save_story

USER_STORY_TEMPLATE = (
    "# {title}\n\n"
    "## Description\n"
    "{description}\n\n"
    "## Acceptance Criteria\n"
    "{acceptance_criteria}\n\n"
    "Dependencies: {dependencies}\n\n"
    "Priority: {priority}"
)


class UserStoryMinimal(BaseModel):
    """The agile user story simple data"""

    Title: str = Field(
        ...,
        description="The title of the user story.",
    )
    Description: str = Field(
        ...,
        description="A brief description of the functionality.",
    )


class UserStoriesMinimal(BaseModel):
    """The agile user stories simple data"""

    Stories: list[UserStoryMinimal] = Field(
        ...,
        description="A list of user stories with Title and Description.",
    )


class UserStory(BaseModel):
    """The agile user story data"""

    Title: str = Field(
        ...,
        description="The title of the user story.",
    )
    Description: str = Field(
        ...,
        description="A brief description of the functionality.",
    )
    AcceptanceCriteria: str = Field(
        ...,
        description="Acceptance criteria for the user story.",
    )
    Dependencies: str = Field(
        default="",
        description="Dependencies.",
    )

    def to_template_string(self) -> str:
        """Return the user story as a formatted string using the template."""
        return USER_STORY_TEMPLATE.format(
            title=self.Title,
            description=self.Description,
            acceptance_criteria=self.AcceptanceCriteria,
            dependencies=self.Dependencies,
            priority="",
        )


class State(TypedDict):
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
        "problem_text": problem_text,
        "stories_minimal": [],
        "stories": [],
        "llm": llm,
    }


def get_stories_minimal(state: State) -> State:
    """
    Analyzes the problem description and extracts a list of user story names.

    Args:
        state (State): The current state containing the problem description and LLM.

    Returns:
        dict: Updated state with 'stories_name' as a list of story titles.
    """
    problem_desc = state["problem_text"]
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert agile analyst. "
                "Given the following problem description, extract a list of possible user stories. "
                "Return ONLY a Python list of short user story titles (as strings), nothing else.",
            ),
            ("human", "{problem_desc}"),
        ]
    )

    llm = state["llm"]
    structured_llm = llm.with_structured_output(UserStoriesMinimal)
    prompt = prompt_template.invoke({"problem_desc": problem_desc})
    # We expect the LLM to return a Python list of strings
    result = structured_llm.invoke(prompt)
    state["stories_minimal"] = result.Stories

    for story in state["stories_minimal"]:
        logging.debug(story.Title)
        logging.debug(story.Description)
        logging.debug("-----")

    return state


def refine_stories(state: State) -> State:
    """
    Refines each user story by adding detailed information.

    Args:
        state (State): The current state containing minimal user stories and LLM.

    Returns:
        State: Updated state with detailed user stories.
    """
    llm = state["llm"]
    structured_llm = llm.with_structured_output(UserStory)

    detailed_stories = []
    for story in state["stories_minimal"]:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert agile analyst. "
                    "Given the following user story title and description, "
                    "provide a detailed user story with all fields filled out. "
                    "Return the result as a JSON object matching the UserStory schema.",
                ),
                (
                    "human",
                    "User Story Title: {title}\n\n"
                    "Description: {description}\n\n"
                    "Provide the following fields:\n"
                    "- Role\n"
                    "- Feature\n"
                    "- Benefit\n"
                    "- Acceptance Criteria\n"
                    "- Constraints\n"
                    "- Performance\n"
                    "- Security\n"
                    "- Dependencies\n"
                    "- Priority\n"
                    "- Estimate\n"
                    "- Attachments",
                ),
            ]
        )
        prompt = prompt_template.invoke(
            {"title": story.Title, "description": story.Description}
        )
        detailed_story = structured_llm.invoke(prompt)
        detailed_stories.append(detailed_story)

    state["stories"] = detailed_stories
    return state


def save_stories(state: State):
    """
    Saves the note and its metadata to the storage.

    Args:
        state (State): The state containing the note and metadata.
    """

    stories = state["stories"]
    for story in stories:
        save_story(story)
