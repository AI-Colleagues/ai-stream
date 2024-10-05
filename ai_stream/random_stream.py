"""App page for Random Stream."""

import streamlit as st
from ai_stream import TESTING
from ai_stream.components.messages import InputWidget
from ai_stream.components.messages import UserMessage
from ai_stream.components.random_assistant import generate_random_response
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


def render_history(history: list):
    """Display chat history."""
    for i, entry in enumerate(history):
        if hasattr(entry, "disable") and i != len(history) - 1:
            entry.disable()
        entry.render()


def check_block_chat_input(history: list):
    """Check waiting for input."""
    if history:
        entry = history[-1]
        if isinstance(entry, InputWidget) and not entry.disabled and not entry.value:
            return True
    return False


@ensure_app_state
def main(app_state: AppState):
    """App layout."""
    render_history(app_state.history)
    disable_input = check_block_chat_input(app_state.history)
    user_message_text = st.chat_input(
        placeholder="Please type input above" if disable_input else "Type your message",
        disabled=disable_input,
    )
    if user_message_text:
        user_message = UserMessage(user_message_text)
        app_state.history.append(user_message)

        assistant_response = generate_random_response(user_message_text, len(app_state.history))
        app_state.history.append(assistant_response)

        st.rerun()


if not TESTING:
    main()
