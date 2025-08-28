import streamlit as st
from config import load_config
from agent import create_stories, read_story
from storage import remove_story_by_title, remove_all_story, get_story_titles


def main():
    load_config()
    st.title("AI Agile Dev")

    menu = ["Create Stories", "List Stories", "View Story", "Remove Story"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Create Stories":
        st.subheader("Create User Stories")
        provider = st.text_input("Provider", "google_genai")
        model = st.text_input("Model", "gemini-1.5-flash-latest")
        doc_path = st.text_input("Path to documentation file")
        minimal = st.checkbox("Only extract minimal user story names without details")

        if st.button("Create"):
            if doc_path:
                with st.spinner("Creating stories..."):
                    create_stories(provider, model, doc_path, minimal)
                st.success("Stories created successfully.")
            else:
                st.error("Please provide the path to the documentation file.")

    elif choice == "List Stories":
        st.subheader("All User Stories")
        titles = get_story_titles()
        if titles:
            for title in titles:
                st.write(f"- {title}")
        else:
            st.info("No stories found.")

    elif choice == "View Story":
        st.subheader("View User Story")
        title = st.text_input("Title of the user story to retrieve")
        if st.button("View"):
            if title:
                read_story(title)
            else:
                st.error("Please provide a title.")

    elif choice == "Remove Story":
        st.subheader("Remove User Story")

        removal_choice = st.radio(
            "Choose removal option:", ("Remove by Title", "Remove All Stories")
        )

        if removal_choice == "Remove by Title":
            titles = get_story_titles()
            title_to_remove = st.selectbox("Select a story to remove:", titles)
            if st.button("Remove Story"):
                if title_to_remove:
                    removed = remove_story_by_title(title_to_remove)
                    if removed:
                        st.success(f"Story '{title_to_remove}' removed.")
                    else:
                        st.error(f"Story '{title_to_remove}' not found.")
                else:
                    st.warning("Please select a story to remove.")

        elif removal_choice == "Remove All Stories":
            if st.button("Remove All Stories"):
                remove_all_story()
                st.success("All stories removed.")


if __name__ == "__main__":
    main()
