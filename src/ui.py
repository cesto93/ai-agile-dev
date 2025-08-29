import streamlit as st
import logging
from src.config import (
    GoogleGenAIModel,
    ModelProvider,
    OllamaModel,
    load_config,
)
from src.agent import create_stories
from src.storage import (
    edit_story,
    get_story_by_title,
    remove_story_by_title,
    remove_all_story,
    get_story_titles,
    rename_story,
)


def initialize_session_state():
    """Initializes the session state variables."""
    if "page" not in st.session_state:
        st.session_state.page = "create"
    if "is_editing" not in st.session_state:
        st.session_state.is_editing = False
    if "is_renaming" not in st.session_state:
        st.session_state.is_renaming = False
    if "selected_story" not in st.session_state:
        st.session_state.selected_story = None
    if "provider" not in st.session_state:
        st.session_state.provider = ModelProvider.GOOGLE_GENAI.value
    if "model" not in st.session_state:
        st.session_state.model = GoogleGenAIModel.GEMINI_2_5_FLASH_LITE.value
    if "log_level" not in st.session_state:
        st.session_state.log_level = "INFO"


def reset_page_states(page=None):
    """Resets editing, renaming, and selected story states."""
    st.session_state.is_editing = False
    st.session_state.is_renaming = False
    st.session_state.selected_story = None
    if page:
        st.session_state.page = page


def render_configuration():
    """Renders the configuration options in the sidebar."""

    def on_provider_change():
        provider = st.session_state.provider
        if provider == ModelProvider.GOOGLE_GENAI.value:
            st.session_state.model = GoogleGenAIModel.GEMINI_2_5_FLASH_LITE.value
        elif provider == ModelProvider.OLLAMA.value:
            st.session_state.model = OllamaModel.GEMMA_3_8B.value

    def on_log_level_change():
        log_level = st.session_state.log_level
        logging.getLogger().setLevel(log_level)

    provider = st.selectbox(
        "Provider",
        options=[p.value for p in ModelProvider],
        key="provider",
        on_change=on_provider_change,
    )

    if provider == ModelProvider.GOOGLE_GENAI.value:
        model_options = [m.value for m in GoogleGenAIModel]
    elif provider == ModelProvider.OLLAMA.value:
        model_options = [m.value for m in OllamaModel]
    else:
        model_options = []

    st.selectbox("Model", options=model_options, key="model")

    st.selectbox(
        "Log Level",
        options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        key="log_level",
        on_change=on_log_level_change,
    )


def render_sidebar():
    """Renders the sidebar contents."""
    st.sidebar.title("Menu")

    with st.sidebar.expander("Configuration"):
        render_configuration()

    if st.sidebar.button("Create Stories"):
        reset_page_states("create")
        st.rerun()

    if st.sidebar.button("Remove Stories"):
        reset_page_states("remove")
        st.rerun()

    st.sidebar.subheader("User Stories")
    story_titles = get_story_titles()

    if story_titles:
        for title in story_titles:
            if st.sidebar.button(title, key=f"view_{title}"):
                st.session_state.is_editing = False
                st.session_state.is_renaming = False
                st.session_state.selected_story = title
                st.rerun()
    else:
        st.sidebar.info("No stories found.")


def render_story_view_mode(title: str, content: str):
    """Renders the story in view mode with options to edit, rename, or remove."""
    st.markdown(content)
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Edit", key=f"edit_{title}"):
            st.session_state.is_editing = True
            st.session_state.is_renaming = False
            st.rerun()
    with col2:
        if st.button("Rename", key=f"rename_{title}"):
            st.session_state.is_renaming = True
            st.session_state.is_editing = False
            st.rerun()
    with col3:
        if st.button("Remove this story", key=f"rm_{title}"):
            remove_story_by_title(title)
            st.success(f"Story '{title}' removed.")
            st.session_state.selected_story = None
            st.rerun()


def render_story_edit_mode(title: str, content: str):
    """Renders the story in edit mode."""
    edited_content = st.text_area("Edit Story", content, height=450)
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Save Changes", key=f"save_{title}"):
            edit_story(title, edited_content)
            st.success(f"Story '{title}' edited.")
            st.session_state.is_editing = False
            st.rerun()
    with col2:
        if st.button("View Mode", key=f"view_mode_{title}"):
            st.session_state.is_editing = False
            st.rerun()


def render_story_rename_mode(title: str):
    """Renders the story in rename mode."""
    st.subheader(f"Rename Story: '{title}'")
    new_title = st.text_input("New title", value=title)
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Save", key=f"save_rename_{title}"):
            if not new_title.strip():
                st.error("Title cannot be empty.")
            elif new_title != title and new_title in get_story_titles():
                st.error(f"A story with title '{new_title}' already exists.")
            else:
                rename_story(title, new_title)
                st.success(f"Story '{title}' renamed to '{new_title}'.")
                st.session_state.is_renaming = False
                st.session_state.selected_story = new_title
                st.rerun()
    with col2:
        if st.button("Cancel", key=f"cancel_rename_{title}"):
            st.session_state.is_renaming = False
            st.rerun()


def render_selected_story():
    """Renders the selected story in view, edit, or rename mode."""
    title = st.session_state.selected_story
    content = get_story_by_title(title)
    if content:
        if st.session_state.is_editing:
            render_story_edit_mode(title, content)
        elif st.session_state.is_renaming:
            render_story_rename_mode(title)
        else:
            render_story_view_mode(title, content)
    else:
        st.error(f"Story '{title}' not found. It may have been removed.")
        reset_page_states("create")
        st.rerun()


def render_create_page():
    """Renders the page for creating new user stories."""
    st.subheader("Create User Stories")
    uploaded_file = st.file_uploader("Upload documentation file", type=["md", "txt"])

    doc_content = ""
    if uploaded_file:
        doc_content = uploaded_file.getvalue().decode("utf-8")
        st.text_area("Documentation Content", doc_content, height=300)

    minimal = st.checkbox("Only extract minimal user story names without details")

    if st.button("Create"):
        if uploaded_file and st.session_state.model:
            with st.spinner("Creating stories..."):
                create_stories(
                    st.session_state.provider,
                    st.session_state.model,
                    doc_content,
                    minimal,
                )
            st.success("Stories created successfully.")
            st.rerun()
        elif not uploaded_file:
            st.error("Please upload a documentation file.")
        else:
            st.error("No model available for the selected provider.")


def render_remove_page():
    """Renders the page for removing all stories."""
    st.subheader("Remove All Stories")
    if st.button("Remove All Stories"):
        remove_all_story()
        st.success("All stories removed.")
        reset_page_states()
        st.rerun()


def render_main_panel():
    """Renders the main panel based on the current page or selected story."""
    if st.session_state.selected_story:
        render_selected_story()
    elif st.session_state.page == "create":
        render_create_page()
    elif st.session_state.page == "remove":
        render_remove_page()


def main():
    """Main function to run the Streamlit app."""
    load_config()
    st.title("AI Agile Dev")

    initialize_session_state()
    # Set initial log level from session state
    logging.getLogger().setLevel(st.session_state.log_level)

    render_sidebar()
    render_main_panel()


if __name__ == "__main__":
    main()
