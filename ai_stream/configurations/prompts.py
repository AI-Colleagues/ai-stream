"""Configuration page for prompts."""

from collections import OrderedDict
import streamlit as st
from code_editor import code_editor
from pynamodb.exceptions import DoesNotExist
from ai_stream import TESTING
from ai_stream.db.aws import PromptsTable
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


def save_prompt(app_state: AppState, prompt_id: str, prompt_name: str, prompt_value: str) -> None:
    """Save prompt and update assistants if needed."""
    try:
        existing_prompt = PromptsTable.get(hash_key=prompt_id)
    except DoesNotExist:
        existing_prompt = None
    if existing_prompt:
        # Update existing prompt
        existing_prompt.update(actions=[PromptsTable.value.set(prompt_value)])
        if existing_prompt.used_by:
            for assistant_id in existing_prompt.used_by:
                app_state.openai_client.beta.assistants.update(
                    assistant_id, instructions=prompt_value
                )
        st.success(f"Prompt has been updated with name {prompt_name} and ID {prompt_id}.")
    else:
        # Save new prompt to DB
        item = PromptsTable(id=prompt_id, name=prompt_name, used_by=[], value=prompt_value)
        item.save()
        st.success(f"Prompt has been saved with name {prompt_name} and ID {prompt_id}.")
        # Update app_state.prompts
        app_state.prompts[prompt_id] = prompt_name


@ensure_app_state
def main(app_state: AppState) -> None:
    """App layout."""
    st.title("OpenAI Prompts")

    if st.button("New Prompt"):
        new_id = create_id()
        app_state.prompts = OrderedDict([(new_id, "NewPrompt")] + list(app_state.prompts.items()))

    prompt_id2name = app_state.prompts
    if not prompt_id2name:
        st.warning("No prompts yet. Click 'New Prompt' to create one.")
        st.stop()

    prompt_id = st.sidebar.selectbox(
        "Select Prompt",
        list(prompt_id2name.keys()),
        format_func=lambda x: prompt_id2name[x],
    )
    prompt_name = prompt_id2name[prompt_id]
    prompt = PromptsTable.get(hash_key=prompt_id)
    prompt_value = prompt.value
    used_by = prompt.used_by
    st.sidebar.caption(f"ID: {prompt_id}")

    # Display text input and text area for editing
    new_name = st.text_input("Prompt Name", value=prompt_name)
    st.write(
        "Press `Control + Enter` (Windows) or `Command + Enter` (Mac) " "to load the changes."
    )
    code = code_editor(prompt_value, lang="markdown", height=500)
    prompt_value = code["text"] or prompt_value
    # Display Markdown of the input texts
    st.markdown("### Preview")
    st.markdown(prompt_value)

    # Save Prompt button
    if st.button("Save Prompt", disabled=not (prompt_value and new_name)):
        save_prompt(app_state, prompt_id, new_name, prompt_value)

    # Add Delete Prompt button
    if prompt_id and st.button("Delete Prompt"):
        try:
            prompt = PromptsTable.get(hash_key=prompt_id)
            prompt.delete()
            st.success(f"Prompt '{prompt_name}' has been deleted.")
            # Remove from app_state.prompts
            if prompt_id in app_state.prompts:
                del app_state.prompts[prompt_id]
            # Reset prompt selection
        except DoesNotExist:
            st.error("Prompt not found.")

    st.subheader("Used By:")
    if used_by:
        for asst in used_by:
            st.write(f"`{asst}`")


if not TESTING:
    main()
