"""Configuration page for prompts."""

import streamlit as st
from pynamodb.exceptions import DoesNotExist
from ai_stream import TESTING
from ai_stream.db.aws import PromptsTable
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


def edit_prompt(
    app_state: AppState, prompt: str, prompt_name: str, prompt_id: str
) -> None:
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
        try:
            existing_prompt = PromptsTable.get(
                hash_key=prompt_id, range_key=prompt_name
            )
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
            st.success(
                f"Prompt has been updated with name {prompt_name} and ID {prompt_id}."
            )
        else:
            # Save new prompt to DB
            item = PromptsTable(
                id=prompt_id, name=prompt_name, used_by=[], value=prompt_value
            )
            item.save()
            st.success(
                f"Prompt has been saved with name {prompt_name} and ID {prompt_id}."
            )


def review_prompt(prompt: str) -> None:
    """Review the given prompt."""
    st.markdown(prompt)


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main layout."""
    st.title("OpenAI Prompts")
    # Get all prompt names and ids from DB
    prompt_id2name = app_state.prompts
    prompt_id = st.sidebar.selectbox(
        "Select Prompt", prompt_id2name, format_func=lambda x: prompt_id2name[x]
    )
    # Get selected prompt from DB
    if not prompt_id:
        prompt_value = ""
        prompt_name = ""
        prompt_id = create_id()
        used_by = []
        st.warning("No prompts yet.")
    else:
        prompt_name = prompt_id2name[prompt_id]
        prompt = PromptsTable.get(hash_key=prompt_id, range_key=prompt_name)
        prompt_value = prompt.value
        used_by = prompt.used_by

        st.sidebar.caption(f"ID: {prompt_id}")
    edit_delete = st.checkbox("Edit/Delete")
    if edit_delete:
        edit_prompt(app_state, prompt_value, prompt_name, prompt_id)
    else:
        review_prompt(prompt_value)

    st.subheader("Used By:")
    if used_by:
        for asst in used_by:
            st.write(f"`{asst}`")


if not TESTING:
    main()
