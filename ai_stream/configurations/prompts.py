"""Configuration page for prompts."""

import streamlit as st
from ai_stream import TESTING
from ai_stream.utils import create_id


def edit_prompt(prompt: str, prompt_name: str, prompt_id: str = ""):
    """Edit the given prompt."""
    if st.checkbox("New Prompt"):
        prompt_value = st.text_area("Edit Prompt", value="", height=500)
        prompt_name = st.text_input("Prompt Name", "New Prompt")
        prompt_id = create_id()
    else:
        prompt_value = st.text_area("Edit Prompt", value=prompt, height=500)
        prompt_name = st.text_input("Prompt Name", prompt_name)
    if st.button("Save", disabled=not (prompt_value and prompt_name)):
        # Save to DB
        st.success(f"Prompt has been saved with name {prompt_name} and ID {prompt_id}.")
        # st.stop()


def review_prompt(prompt: str) -> None:
    """Review the given prompt."""
    st.markdown(prompt)


def main():
    """Main layout."""
    # Get all prompt names and ids from DB
    # prompts = PromptsTable.scan(attributes_to_get="name, id")
    # prompt_name_ids = {prompt.id: prompt.name for prompt in prompts}
    prompt_id2name = {
        "prompt1": "Prompt 1",
        "prompt2": "Prompt 2",
    }
    prompts = {
        "prompt1": "You are a helpful assistant.",
        "prompt2": "You are a helpful assistant too.",
    }
    prompt_id = st.sidebar.selectbox(
        "Prompts", prompt_id2name, format_func=lambda x: prompt_id2name[x]
    )
    # Get selected prompt from DB
    # prompt = PromptsTable.get(hash_key=prompt_choice)
    prompt = prompts[prompt_id]

    st.sidebar.caption(f"ID: {prompt_id}")
    prompt_name = prompt_id2name[prompt_id]
    prompt_value = prompt

    edit_delete = st.checkbox("Edit/Delete")
    if edit_delete:
        edit_prompt(prompt_value, prompt_name, prompt_id)
    else:
        review_prompt(prompt)


if not TESTING:
    main()
