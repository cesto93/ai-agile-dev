from typing import TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from src.storage import save_note, save_story
import os

USER_STORY_TEMPLATE = (
    "Titolo:\n"
    "{title}\n\n"
    "[Breve descrizione della funzionalità]\n"
    "{description}\n\n"
    "User Story:\n\n"
    "Come {role}\n"
    "voglio {feature}\n"
    "in modo da {benefit}\n\n"
    "Criteri di accettazione (Acceptance Criteria):\n"
    "{acceptance_criteria}\n\n"
    "Note tecniche (facoltative):\n\n"
    "Vincoli tecnologici: {constraints}\n\n"
    "Performance: {performance}\n\n"
    "Sicurezza: {security}\n\n"
    "Dipendenze: {dependencies}\n\n"
    "Priorità:\n\n"
    "{priority}\n\n"
    "Stima:\n\n"
    "{estimate}\n\n"
    "Allegati / Mockup:\n\n"
    "{attachments}\n"
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
    Role: str = Field(
        ...,
        description="The user role (e.g., 'utente', 'admin').",
    )
    Feature: str = Field(
        ...,
        description="The feature the user wants.",
    )
    Benefit: str = Field(
        ...,
        description="The benefit the user gets.",
    )
    AcceptanceCriteria: str = Field(
        ...,
        description="Acceptance criteria for the user story.",
    )
    Constraints: str = Field(
        default="",
        description="Technological constraints.",
    )
    Performance: str = Field(
        default="",
        description="Performance requirements.",
    )
    Security: str = Field(
        default="",
        description="Security requirements.",
    )
    Dependencies: str = Field(
        default="",
        description="Dependencies.",
    )
    Priority: str = Field(
        default="",
        description="Priority.",
    )
    Estimate: str = Field(
        default="",
        description="Estimate.",
    )
    Attachments: str = Field(
        default="",
        description="Attachments or mockups.",
    )

    def to_template_string(self) -> str:
        """Return the user story as a formatted string using the template."""
        return USER_STORY_TEMPLATE.format(
            title=self.Title,
            description=self.Description,
            role=self.Role,
            feature=self.Feature,
            benefit=self.Benefit,
            acceptance_criteria=self.AcceptanceCriteria,
            constraints=self.Constraints,
            performance=self.Performance,
            security=self.Security,
            dependencies=self.Dependencies,
            priority=self.Priority,
            estimate=self.Estimate,
            attachments=self.Attachments,
        )


class State(TypedDict):
    problem_text: str
    stories_name: list[str]
    stories: list[UserStory]
    llm: BaseChatModel


def create_agent():
    """
    Creates a Google Generative AI agent with the specified model.

    Args:
        model (str): The model to use for the agent.

    Returns:
        ChatGoogleGenerativeAI: An instance of the Google Generative AI agent.
    """

    graph_builder = StateGraph(State)
    graph_builder.add_node("get_stories", get_stories)
    graph_builder.add_node("save_note_action", save_stories_action)

    graph_builder.add_edge(START, "paraphrase_text")
    graph_builder.add_edge("paraphrase_text", "extract_metadata")
    graph_builder.add_edge("extract_metadata", "save_note_action")
    graph_builder.add_edge("save_note_action", END)
    graph = graph_builder.compile()

    return graph


def get_initial_state(provider: str, model: str, doc_path: str) -> State:
    """
    Returns the initial state for the agent.

    Args:
        provider (str): The provider for the language model.
        model (str): The model to use.
        docPath (str): The path to the document to read.

    Returns:
        State: The initial state containing the document and llm.
    """
    llm = init_chat_model(f"{provider}:{model}")
    with open(doc_path, "r", encoding="utf-8") as f:
        problem_text = f.read()
    return {
        "problem_text": problem_text,
        "stories_name": [],
        "stories": [],
        "llm": llm,
    }


def get_stories(state: State):
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
    prompt = prompt_template.invoke({"problem_desc": problem_desc})
    # We expect the LLM to return a Python list of strings
    result = llm.invoke(prompt)
    # Try to safely evaluate the result as a Python list
    import ast

    try:
        stories_name = ast.literal_eval(result)
        if not isinstance(stories_name, list):
            raise ValueError
    except Exception:
        raise ValueError("LLM did not return a valid list of user story names.")

    return {**state, "stories_name": stories_name}


def save_stories_action(state: State):
    """
    Saves the note and its metadata to the storage.

    Args:
        state (State): The state containing the note and metadata.
    """

    stories = state["stories"]
    for story in stories:
        save_story(story)
