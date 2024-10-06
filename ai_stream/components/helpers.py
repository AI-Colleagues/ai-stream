"""Miscellaneous components."""

import streamlit as st
from ai_stream.components.messages import UserMessage


def display_used_by(used_by: list[str]) -> None:
    """Display the assistant IDs that uses this function/prompt. `None` if empty."""
    st.subheader("Used By:")
    if used_by:
        st.markdown(", ".join([f"`{asst}`" for asst in used_by]))
    else:
        st.markdown("`None`")


def select_assistant(assistants: dict) -> tuple:
    """Select assistant and return its ID and name."""
    if not assistants:
        st.warning("No assistants yet. Click 'New Assistant' to create one.")
        st.stop()

    assistant_id = st.sidebar.selectbox(
        "Select Assistant",
        options=assistants,
        format_func=lambda x: assistants[x],
        key="select_asst",
    )
    st.sidebar.caption(f"ID: {assistant_id}")

    return assistant_id, assistants[assistant_id]


def render_history(history: list):
    """Display chat history."""
    last_user_msg_index = None
    for i, entry in enumerate(history):
        if isinstance(entry, UserMessage):
            last_user_msg_index = i

    if last_user_msg_index is not None:
        for entry in history[:last_user_msg_index]:
            if hasattr(entry, "disable"):
                entry.disable()
    for entry in history:
        entry.render()
