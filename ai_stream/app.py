"""Main entry for AI Stream."""

import os
import streamlit as st
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_openai import ChatOpenAI
from openai import AssistantEventHandler
from openai import OpenAI
from openai.types.beta.threads import Text
from streamlit.runtime.uploaded_file_manager import UploadedFile
from typing_extensions import override
from ai_stream.ui_as_tools import UI_TOOLS
from ai_stream.ui_as_tools import instantiate_ui_tools
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


class EventHandler(AssistantEventHandler):
    """Event handler for OpenAI Assistants."""

    def __init__(self, *args, app_state: AppState, **kwargs):
        """Initialise."""
        self.app_state = app_state
        super().__init__(*args, **kwargs)

    @override
    def on_text_created(self, text) -> None:
        print("\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_text_done(self, text: Text) -> None:
        """Done generating."""
        self.app_state.chat_history.append((ASSISTANT_LABEL, {}, text.value))

    def on_tool_call_created(self, tool_call):
        """Started tool call."""
        print(f"\nassistant > {tool_call.type}\n", flush=True)

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


def get_response_with_file_analysis(
    app_state: AppState, files: list[UploadedFile]
) -> None:
    """Call OpenAI assistant directly with code interpreter."""
    client = OpenAI()
    file_ids = []

    # Upload files to OpenAI
    for file in files:
        uploaded = client.files.create(file=file.getvalue(), purpose="assistants")
        file_ids.append(uploaded.id)

    # Create an assistant using the file ID
    assistant = client.beta.assistants.create(
        instructions=SYSTEM_PROMPT,
        model=MODEL_NAME,
        tools=[{"type": "code_interpreter"}],
        tool_resources={"code_interpreter": {"file_ids": file_ids}},
    )
    thread = client.beta.threads.create(
        messages=[
            {
                "role": msg[0],
                "content": msg[1] if msg[0] == USER_LABEL else msg[2],
                # "attachments": [  # TODO: only using the last file now
                #     {"file_id": file_ids[-1], "tools": [{"type": "code_interpreter"}]}
                # ],
            }
            for msg in app_state.chat_history
        ]
    )
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler(app_state=app_state),
    ) as stream:
        stream.until_done()

    st.rerun()


def get_response(
    app_state: AppState,
    model_name: str = MODEL_NAME,
) -> None:
    """Send messages to backend to get an LLM response with UI rendering."""
    if "files" in app_state.recent_tool_output:
        return get_response_with_file_analysis(
            app_state, app_state.recent_tool_output["files"]
        )

    msgs = [
        msg if msg[0] != ASSISTANT_LABEL else (msg[0], msg[2])
        for msg in app_state.chat_history
    ]  # Discard tool calls
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            *msgs,
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    llm = ChatOpenAI(model=model_name)
    tools = instantiate_ui_tools()

    agent = create_tool_calling_agent(llm, tools, chat_prompt)
    agent_executor = AgentExecutor(
        agent=agent,  # type: ignore
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
    )
    response = agent_executor.invoke({})

    # Return tool calls and agent response, but tool running (rendering) is
    # called at the frontend
    # TODO: Sometimes the same tool was generated continuously
    # TODO: currently only support one tool at a timex
    tool_call = {}
    if "intermediate_steps" in response:
        for action in response["intermediate_steps"]:
            tool_call[action[0].tool] = action[0].tool_input
            break

    bot_response = ""
    if "output" in response:
        bot_response = response["output"]
        app_state.chat_history.append((ASSISTANT_LABEL, tool_call, bot_response))

    st.rerun()  # This is necessary to trigger the history display in time


def display_history(app_state: AppState) -> None:
    """Display all history messages."""
    history = app_state.chat_history
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

        get_response(app_state)


if not TESTING:
    main()
