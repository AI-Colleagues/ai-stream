"""App page for Random Stream."""

import streamlit as st
from ai_stream import TESTING
from ai_stream.components.messages import InputWidgetMessage
from ai_stream.components.messages import UserMessage
from ai_stream.components.random_assistant import generate_random_response


def initialize_session_state():
    """Initialise session state."""
    if "history" not in st.session_state:
        st.session_state.history = []
        st.session_state.widget_counter = 0


def render_history():
    """Display chat history."""
    for i, entry in enumerate(st.session_state.history):
        if hasattr(entry, "disable") and i != len(st.session_state.history) - 1:
            entry.disable()
        entry.render()


def check_block_chat_input():
    """Check waiting for input."""
    for entry in st.session_state.history:
        if isinstance(entry, InputWidgetMessage) and not entry.disabled and not entry.value:
            return True
    return False


def main():
    """App layout."""
    initialize_session_state()
    render_history()
    disable_input = check_block_chat_input()
    user_message_text = st.chat_input(
        placeholder="Please type input above" if disable_input else "Type your message",
        disabled=disable_input,
    )
    if user_message_text:
        user_message = UserMessage(user_message_text)
        st.session_state.history.append(user_message)

        assistant_response, st.session_state.widget_counter = generate_random_response(
            user_message_text, st.session_state.widget_counter
        )
        st.session_state.history.append(assistant_response)

        st.rerun()


if not TESTING:
    main()
