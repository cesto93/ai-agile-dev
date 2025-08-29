import streamlit as st
from config import load_config
from agent import create_stories
from storage import (
    get_story_by_title,
    remove_story_by_title,
    remove_all_story,
    get_story_titles,
)


def main():
    load_config()
    st.title("AI Agile Dev")

    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "create"
    if "is_editing" not in st.session_state:
        st.session_state.is_editing = False
    if "selected_story" not in st.session_state:
        st.session_state.selected_story = None

    # --- Sidebar ---
    st.sidebar.title("Menu")

    if st.sidebar.button("Create Stories"):
        st.session_state.page = "create"
        st.session_state.is_editing = False
        st.session_state.selected_story = None
        st.rerun()

    if st.sidebar.button("Remove Stories"):
        st.session_state.page = "remove"
        st.session_state.is_editing = False
        st.session_state.selected_story = None
        st.rerun()

    st.sidebar.subheader("User Stories")
    story_titles = get_story_titles()

    if story_titles:
        for title in story_titles:
            if st.sidebar.button(title, key=f"view_{title}"):
                st.session_state.is_editing = (
                    False  # Reset edit mode when selecting a new story
                )
                st.session_state.selected_story = title
                st.rerun()
    else:
        st.sidebar.info("No stories found.")

    # --- Main Panel ---
    if st.session_state.selected_story:
        title = st.session_state.selected_story
        content = get_story_by_title(title)
        if content:  # Check if content is not None
            if st.session_state.is_editing:
                edited_content = st.text_area("Edit Story", content, height=450)
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("Save Changes", key=f"save_{title}"):
                        st.warning("Saving edited content is not yet implemented.")
                        # Here you would typically call a save function, e.g., save_story(title, edited_content)
                with col2:
                    if st.button("View Mode", key=f"view_mode_{title}"):
                        st.session_state.is_editing = False
                        st.rerun()
            else:
                st.markdown(content)
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("Edit", key=f"edit_{title}"):
                        st.session_state.is_editing = True
                        st.rerun()
                with col2:
                    if st.button("Remove this story", key=f"rm_{title}"):
                        remove_story_by_title(title)
                        st.success(f"Story '{title}' removed.")
                        st.session_state.selected_story = None
                        st.rerun()
        else:
            st.error(f"Story '{title}' not found. It may have been removed.")
            st.session_state.selected_story = None
            st.session_state.page = "create"
            st.rerun()

    elif st.session_state.page == "create":
        st.subheader("Create User Stories")
        provider = st.text_input("Provider", "google_genai")
        model = st.text_input("Model", "gemini-2.5-flash-lite")
        uploaded_file = st.file_uploader(
            "Upload documentation file", type=["md", "txt"]
        )
        minimal = st.checkbox("Only extract minimal user story names without details")

        if st.button("Create"):
            if uploaded_file:
                doc_content = uploaded_file.getvalue().decode("utf-8")
                with st.spinner("Creating stories..."):
                    create_stories(provider, model, doc_content, minimal)
                st.success("Stories created successfully.")
                st.rerun()
            else:
                st.error("Please upload a documentation file.")

    elif st.session_state.page == "remove":
        st.subheader("Remove All Stories")
        if st.button("Remove All Stories"):
            remove_all_story()
            st.success("All stories removed.")
            st.session_state.selected_story = None
            st.rerun()


if __name__ == "__main__":
    main()
