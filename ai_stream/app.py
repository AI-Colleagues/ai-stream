"""Main entry for AI Stream."""

import json
import logging
import os
import streamlit as st
from openai import AssistantEventHandler
from openai import OpenAI
from openai.types.beta.threads import Text
from openai.types.beta.threads.runs import ToolCall
from streamlit.delta_generator import DeltaGenerator
from typing_extensions import override
from ai_stream.ui_as_tools import UI_TOOLS
from ai_stream.ui_as_tools import tools_to_openai_functions
from ai_stream.utils import AppState
from ai_stream.utils import ensure_app_state


ASSISTANT_LABEL = "assistant"
USER_LABEL = "user"
TESTING = int(os.environ.get("TESTING", "0"))
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
client = OpenAI()


class UIAssistantEventHandler(AssistantEventHandler):
    """Event handler for UI Assistant."""

    def __init__(
        self, *args, app_state: AppState, st_placeholder: DeltaGenerator, **kwargs
    ):
        """Initialise."""
        self.app_state = app_state
        self.st_placeholder = st_placeholder
        self.running_response = ""
        with self.st_placeholder:
            st.write(PROCESSING_REFRESH)
        super().__init__(*args, **kwargs)

    @override
    def on_text_created(self, text) -> None:
        self.st_placeholder = st.empty()
        self.running_response = ""

    @override
    def on_text_delta(self, delta, snapshot):
        self.running_response += delta.value
        with self.st_placeholder:
            st.write(self.running_response)

    def on_text_done(self, text: Text) -> None:
        """Done generating."""
        self.app_state.chat_history.append((ASSISTANT_LABEL, {}, text.value))

    @override
    def on_tool_call_created(self, tool_call: ToolCall) -> None:
        self.st_placeholder = st.empty()

    def on_tool_call_delta(self, delta, snapshot):
        """Done tool call."""
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print("\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    def on_event(self, event):
        if event.event == "thread.run.requires_action":
            run_id = event.data.id  # Retrieve the run ID from the event data
            with self.st_placeholder.container():
                self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        """Call tools."""
        tool_outputs = []
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            kwargs = json.loads(tool.function.arguments)
            tool_name = tool.function.name.replace("Schema", "")
            logger.info(f"Running tool {tool_name}.")
            UI_TOOLS[tool_name]().render(**kwargs)

            tool_outputs.append({"tool_call_id": tool.id, "output": ""})

        # Submit all tool_outputs at the same time
        response = self.submit_tool_outputs(tool_outputs, run_id)
        self.app_state.chat_history.append(
            (ASSISTANT_LABEL, {tool_name: kwargs}, response)
        )

    def submit_tool_outputs(self, tool_outputs, run_id):
        """Use the submit_tool_outputs_stream helper."""
        with client.beta.threads.runs.submit_tool_outputs_stream(
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
            uploaded = client.files.create(file=file.getvalue(), purpose="assistants")
            file_ids.append(uploaded.id)

        # Create an assistant using the file ID
        assistant = client.beta.assistants.create(
            instructions=SYSTEM_PROMPT,
            model=MODEL_NAME,
            tools=[{"type": "code_interpreter"}],
            tool_resources={"code_interpreter": {"file_ids": file_ids}},
        )
    else:
        tools = tools_to_openai_functions()
        # Create an assistant using the file ID
        assistant = client.beta.assistants.create(
            instructions=SYSTEM_PROMPT,
            model=model_name,
            tools=tools,
        )
    thread = client.beta.threads.create(
        messages=[
            {
                "role": msg[0],
                "content": msg[1] if msg[0] == USER_LABEL else msg[2],
            }
            for msg in app_state.chat_history
        ]
    )
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=UIAssistantEventHandler(
            app_state=app_state, st_placeholder=st_placeholder
        ),
    ) as stream:
        stream.until_done()

    st.rerun()


def display_history(app_state: AppState) -> None:
    """Display all history messages."""
    history = app_state.chat_history  # TODO: Get from OpenAI Thread
    app_state.recent_tool_output.clear()  # Clear previous tool_output
    for i, message in enumerate(history):
        if message[0] == ASSISTANT_LABEL:
            tool_call = message[1]
            response = message[2]
            with st.chat_message(ASSISTANT_LABEL):
                if tool_call:
                    for tool_name, tool_input in tool_call.items():
                        tool_output = UI_TOOLS[tool_name].render(**tool_input)
                        if tool_output and i == len(history) - 1:
                            app_state.recent_tool_output.update(tool_output)
                st.write(response)
        else:
            st.chat_message(message[0]).write(message[1])


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main layout."""
    st.set_page_config(TITLE, page_icon="📱")
    st.title(TITLE)
    display_history(app_state)

    user_input = st.chat_input("Your message")
    if user_input:
        app_state.chat_history.append((USER_LABEL, user_input))
        st.chat_message(USER_LABEL).write(user_input)

        with st.chat_message(ASSISTANT_LABEL):
            get_response(app_state)


if not TESTING:
    main()
