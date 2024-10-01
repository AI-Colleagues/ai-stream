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
    for entry in st.session_state.history:
        entry.render()


def check_waiting_for_input():
    """Check waiting for input."""
    for entry in st.session_state.history:
        if isinstance(entry, InputWidgetMessage) and not entry.user_input_provided:
            return True
    return False


def main():
    """App layout."""
    initialize_session_state()
    render_history()
    if check_waiting_for_input():
        st.stop()

    user_message_text = st.chat_input("Type your message")
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
