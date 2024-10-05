"""Main app for AI Stream."""

import json
import logging
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
from ai_stream import ASSISTANT_LABEL
from ai_stream import TESTING
from ai_stream import USER_LABEL
from ai_stream.components.tools import TOOLS
from ai_stream.components.tools import tools_to_openai_functions
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


TITLE = "AI Stream"
MODEL_NAME = "gpt-4o"
SYSTEM_PROMPT = (
    "You are an AI agent with a lot of tools. Call the right one "
    "according to user instructions."
)

PROCESSING_START = "`Processing`"
PROCESSING_REFRESH = "`Processing...`"


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UIAssistantEventHandler(AssistantEventHandler):
    """Event handler for UI Assistant."""

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
        with self.st_placeholder:
            st.write(snapshot.value)

    @override
    def on_text_done(self, text: Text) -> None:
        self.app_state.history.append((ASSISTANT_LABEL, {}, text.value))

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
            tool_name = tool.function.name.replace("Schema", "")
            logger.info(f"Running tool {tool_name}.")
            # TODO: Displaying here is redundant
            TOOLS[tool_name].render(**kwargs)

            tool_outputs.append({"tool_call_id": tool.id, "output": "Widget displayed to user."})

        # Submit all tool_outputs at the same time
        response = self.submit_tool_outputs(tool_outputs, run_id)
        self.app_state.history.append((ASSISTANT_LABEL, {tool_name: kwargs}, response))

    def submit_tool_outputs(self, tool_outputs: list, run_id: str) -> str:
        """Use the submit_tool_outputs_stream helper."""
        assert self.current_run
        with self.client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            # event_handler=UIAssistantEventHandler(),
        ) as stream:
            res = ""
            with st.empty():
                for text in stream.text_deltas:
                    res += text
                    st.write(res)
            return res


def get_response(
    app_state: AppState,
    model_name: str = MODEL_NAME,
) -> None:
    """Send messages to backend to get an LLM response with UI rendering."""
    st_placeholder = st.empty()
    with st_placeholder:
        st.write(PROCESSING_START)
    if "files" in app_state.recent_tool_output:
        # Use code interpreter assistant
        file_ids = []

        # Upload files to OpenAI
        for file in app_state.recent_tool_output["files"]:
            uploaded = app_state.openai_client.files.create(
                file=file.getvalue(), purpose="assistants"
            )
            file_ids.append(uploaded.id)

        # Create an assistant using the file ID
        assistant = app_state.openai_client.beta.assistants.create(
            instructions=SYSTEM_PROMPT,
            model=MODEL_NAME,
            tools=[{"type": "code_interpreter"}],
            tool_resources={"code_interpreter": {"file_ids": file_ids}},
        )
    else:
        tools = tools_to_openai_functions()
        # Create an assistant using the file ID
        assistant = app_state.openai_client.beta.assistants.create(
            instructions=SYSTEM_PROMPT,
            model=model_name,
            tools=tools,  # type: ignore[arg-type]
        )

    with app_state.openai_client.beta.threads.runs.stream(
        thread_id=app_state.openai_thread_id,
        assistant_id=assistant.id,
        event_handler=UIAssistantEventHandler(app_state=app_state, st_placeholder=st_placeholder),
    ) as stream:
        stream.until_done()

    st.rerun()


def display_history(app_state: AppState) -> None:
    """Display all history messages."""
    history = app_state.history
    app_state.recent_tool_output.clear()  # Clear previous tool_output
    for i, message in enumerate(history):
        if message[0] == ASSISTANT_LABEL:
            tool_call = message[1]
            response = message[2]
            with st.chat_message(ASSISTANT_LABEL):
                if tool_call:
                    for tool_name, tool_input in tool_call.items():
                        tool_output = TOOLS[tool_name].render(**tool_input)
                        if tool_output and i == len(history) - 1:
                            app_state.recent_tool_output.update(tool_output)
                st.write(response)
        else:
            st.chat_message(message[0]).write(message[1])


@ensure_app_state
def main(app_state: AppState) -> None:
    """App layout."""
    st.title(TITLE)
    if not app_state.openai_thread_id:
        thread = app_state.openai_client.beta.threads.create()
        app_state.openai_thread_id = thread.id
    display_history(app_state)

    user_input = st.chat_input("Your message")
    if user_input:
        app_state.history.append((USER_LABEL, user_input))
        st.chat_message(USER_LABEL).write(user_input)
        app_state.openai_client.beta.threads.messages.create(
            app_state.openai_thread_id,
            role="user",
            content=user_input,
        )

        with st.chat_message(ASSISTANT_LABEL):
            get_response(app_state)


if not TESTING:
    main()
