"""Miscellaneous components."""

import json
from typing import override
import streamlit as st
from openai import AssistantEventHandler
from openai.types.beta import AssistantStreamEvent
from openai.types.beta.threads import Run
from openai.types.beta.threads import Text
from openai.types.beta.threads import TextDelta
from openai.types.beta.threads.runs import ToolCall
from openai.types.beta.threads.runs import ToolCallDelta
from streamlit.delta_generator import DeltaGenerator
from ai_stream.components.messages import AssistantMessage
from ai_stream.components.messages import InputWidget
from ai_stream.components.messages import UserMessage
from ai_stream.components.tools import TOOLS
from ai_stream.config import get_logger
from ai_stream.utils.app_state import AppState


PROCESSING_REFRESH = "`Processing...`"
logger = get_logger(__name__)


class StreamAssistantEventHandler(AssistantEventHandler):
    """Event handler for Stream Assistant."""

    def __init__(
        self,
        *args: list,
        app_state: AppState,
        st_placeholder: DeltaGenerator,
        **kwargs: dict,
    ):
        """Initialise."""
        self.app_state = app_state
        self.client = app_state.openai_client
        self.st_placeholder = st_placeholder
        with self.st_placeholder:
            st.write(PROCESSING_REFRESH)
        super().__init__(*args, **kwargs)

    @override
    def on_text_created(self, text: Text) -> None:
        self.st_placeholder = st.empty()

    @override
    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        # TODO: Use streaming with AssistantMessage
        with self.st_placeholder:
            st.write(snapshot.value)

    @override
    def on_text_done(self, text: Text) -> None:
        self.app_state.history.append(AssistantMessage(content=text.value))

    @override
    def on_tool_call_created(self, tool_call: ToolCall) -> None:
        self.st_placeholder = st.empty()

    @override
    def on_tool_call_delta(self, delta: ToolCallDelta, snapshot: ToolCall) -> None:
        # TODO: display code
        if delta.type == "code_interpreter":
            assert delta.code_interpreter
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print("\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    def on_tool_call_done(self, tool_call: ToolCall) -> None:
        # TODO: Store tool type and data for later displaying
        pass

    @override
    def on_event(self, event: AssistantStreamEvent) -> None:
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            with self.st_placeholder.container():
                self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data: Run, run_id: str) -> None:
        """Call tools."""
        tool_outputs = []
        assert data.required_action
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            kwargs = json.loads(tool.function.arguments)
            tool_name = tool.function.name
            logger.info(f"Running tool {tool_name}.")
            # TODO: Displaying here is redundant
            tool_message = TOOLS[tool_name]()
            if issubclass(TOOLS[tool_name], InputWidget):
                kwargs["key"] = f"{tool_name}_{len(self.app_state.history)}"
            tool_message._run(**kwargs)
            self.app_state.history.append(tool_message)

            tool_outputs.append({"tool_call_id": tool.id, "output": f"Displayed a {tool_name}."})

        # Submit all tool_outputs at the same time
        final_response = self.submit_tool_outputs(tool_outputs, run_id)
        self.app_state.history.append(AssistantMessage(content=final_response))

    def submit_tool_outputs(self, tool_outputs: list, run_id: str) -> str:
        """Use the submit_tool_outputs_stream helper."""
        assert self.current_run
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
        ) as stream:
            res = ""
            with st.empty():
                for text in stream.text_deltas:
                    res += text
                    st.write(res)
            return res


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
