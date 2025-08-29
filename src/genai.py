import logging
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

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


def clean_problem_description(llm: BaseChatModel, problem_desc: str) -> str:
    """
    Cleans the problem description by removing irrelevant information.

    Args:
        llm (BaseChatModel): The language model to use for cleaning.
        problem_desc (str): The original problem description.

    Returns:
        str: The cleaned problem description.
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert agile analyst."
                "Given the following problem description, return the text ommitting information not relevant to the use case"
                "Do not change any other word, only delete irrelevant information.",
            ),
            ("human", "{problem_desc}"),
        ]
    )

    prompt = prompt_template.invoke({"problem_desc": problem_desc})
    result = llm.invoke(prompt)
    text = result.content

    # Ensure the result is always a string
    if isinstance(text, list):
        text = "\n".join(str(item) for item in text)

    logging.debug("Original Problem Description:")
    logging.debug(problem_desc)
    logging.debug("Cleaned Problem Description:")
    logging.debug(text)

    return text


def get_stories_minimal(
    llm: BaseChatModel, problem_desc: str
) -> list[UserStoryMinimal]:
    """
    Analyzes the problem description and extracts a list of user story names.

    Args:
        state (State): The current state containing the problem description and LLM.

    Returns:
        dict: Updated state with 'stories_name' as a list of story titles.
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert agile analyst. "
                "Given the following problem description, extract a list of possible user stories. "
                "Return Python list of short user story titles and brief descriptions",
            ),
            ("human", "{problem_desc}"),
        ]
    )

    structured_llm = llm.with_structured_output(UserStoriesMinimal)
    prompt = prompt_template.invoke({"problem_desc": problem_desc})
    # We expect the LLM to return a Python list of strings
    result = structured_llm.invoke(prompt)
    stories = result.Stories

    for story in stories:
        logging.debug(story.Title)
        logging.debug(story.Description)
        logging.debug("-----")

    return stories


def refine_stories(
    llm: BaseChatModel, stories_minimal: list[UserStoryMinimal]
) -> list[UserStory]:
    """
    Refines each user story by adding detailed information.

    Args:
        state (State): The current state containing minimal user stories and LLM.

    Returns:
        State: Updated state with detailed user stories.
    """
    structured_llm = llm.with_structured_output(UserStory)

    detailed_stories = []
    for story in stories_minimal:
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

    return detailed_stories
