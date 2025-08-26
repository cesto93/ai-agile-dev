from typing import TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from src.storage import save_note

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
    note: str
    metadata: NoteMetadata
    llm: BaseChatModel
    action: str


def create_agent():
    """
    Creates a Google Generative AI agent with the specified model.

    Args:
        model (str): The model to use for the agent.

    Returns:
        ChatGoogleGenerativeAI: An instance of the Google Generative AI agent.
    """

    graph_builder = StateGraph(State)
    graph_builder.add_node("summarize_text", summarize_text)
    graph_builder.add_node("paraphrase_text", paraphrase_text)
    graph_builder.add_node("extract_metadata", extract_metadata)
    graph_builder.add_node("save_note_action", save_note_action)

    graph_builder.add_edge(START, "paraphrase_text")
    graph_builder.add_edge("paraphrase_text", "extract_metadata")
    graph_builder.add_edge("extract_metadata", "save_note_action")
    graph_builder.add_edge("save_note_action", END)
    graph = graph_builder.compile()

    return graph


def get_initial_state(model: str, note: str, action: str) -> State:
    """
    Returns the initial state for the agent.

    Returns:
        State: The initial state containing default values.
    """
    llm = init_chat_model(f"google_genai:{model}")
    return {
        "note": note,
        "metadata": NoteMetadata(Title="", Tags=[]),
        "llm": llm,
        "action": action,
    }


def extract_metadata(state: State):
    """
    Extracts metadata from the given text using the provided language model.

    Args:
        llm (ChatGoogleGenerativeAI): The language model to use for metadata extraction.
        text (str): The text from which to extract metadata.

    Returns:
        NoteMetadata: An instance containing the extracted metadata.
    """
    text = state["note"]
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the text. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            ("human", "{text}"),
        ]
    )

    llm = state["llm"]
    structured_llm = llm.with_structured_output(schema=NoteMetadata)
    prompt = prompt_template.invoke({"text": text})
    result = structured_llm.invoke(prompt)
    if isinstance(result, NoteMetadata):
        return {"metadata": result}
    else:
        raise ValueError("The result is not of type NoteMetadata.")


def save_note_action(state: State):
    """
    Saves the note and its metadata to the storage.

    Args:
        state (State): The state containing the note and metadata.
    """

    note = state["note"]
    metadata = state["metadata"]
    save_note(note, metadata.Title, metadata.Tags)
