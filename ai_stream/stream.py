"""Main app for AI Stream."""

import streamlit as st
from ai_stream import ASSISTANT_LABEL
from ai_stream import TESTING
from ai_stream.components.helpers import StreamAssistantEventHandler
from ai_stream.components.helpers import render_history
from ai_stream.components.helpers import select_assistant
from ai_stream.components.messages import UserMessage
from ai_stream.config import get_logger
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


TITLE = "AI Stream"
MODEL_NAME = "gpt-4o-mini"
PROCESSING_START = "`Processing`"

logger = get_logger(__name__)


def get_response(
    app_state: AppState,
    assistant_id: str,
    model_name: str = MODEL_NAME,
) -> None:
    """Send messages to backend to get an LLM response with UI rendering."""
    st_placeholder = st.empty()
    with st_placeholder:
        st.write(PROCESSING_START)
    if "files" in app_state.recent_tool_output:
        # TODO: Needs update
        # Use code interpreter assistant
        file_ids = []

        # Upload files to OpenAI
        for file in app_state.recent_tool_output["files"]:
            uploaded = app_state.openai_client.files.create(
                file=file.getvalue(), purpose="assistants"
            )
            file_ids.append(uploaded.id)

    with app_state.openai_client.beta.threads.runs.stream(
        thread_id=app_state.openai_thread_id,
        assistant_id=assistant_id,
        event_handler=StreamAssistantEventHandler(
            app_state=app_state, st_placeholder=st_placeholder
        ),
    ) as stream:
        stream.until_done()

    st.rerun()


@ensure_app_state
def main(app_state: AppState) -> None:
    """App layout."""
    st.title(TITLE)
    assistant_id, _ = select_assistant(app_state.assistants)
    if not app_state.openai_thread_id:  # One thread per session
        thread = app_state.openai_client.beta.threads.create()
        app_state.openai_thread_id = thread.id
    render_history(app_state.history)

    user_input = st.chat_input("Your message")
    if user_input:
        user_msg = UserMessage(content=user_input)
        app_state.history.append(user_msg)
        user_msg.render()  # Make sure user message displays once sent
        app_state.openai_client.beta.threads.messages.create(
            app_state.openai_thread_id,
            role="user",
            content=user_input,
        )

        with st.chat_message(ASSISTANT_LABEL):
            get_response(app_state, assistant_id)


if not TESTING:
    main()
