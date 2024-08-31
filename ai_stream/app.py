"""Main entry for AI Stream."""

import os
import streamlit as st
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_openai import ChatOpenAI
from ai_stream.ui_as_tools import UI_TOOLS
from ai_stream.ui_as_tools import instantiate_ui_tools
from ai_stream.utils import AppState
from ai_stream.utils import ensure_app_state


ASSISTANT_LABEL = "assistant"
USER_LABEL = "user"
TESTING = int(os.environ.get("TESTING", "0"))
TITLE = "AI Stream"


def get_response(
    app_state: AppState,
    messages: list,
    model_name: str = "gpt-4o",
) -> None:
    """Send messages to backend to get an LLM response with UI rendering."""
    msgs = [
        msg if msg[0] != ASSISTANT_LABEL else (msg[0], msg[2]) for msg in messages
    ]  # Discard tool calls
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an AI agent with a lot of tools. Call the right one "
                "according to user instructions.",
            ),
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


def display_history(history: list[tuple]) -> None:
    """Display all history messages."""
    for message in history:
        if message[0] == ASSISTANT_LABEL:
            tool_call = message[1]
            response = message[2]
            with st.chat_message(ASSISTANT_LABEL):
                if tool_call:
                    for tool_name, tool_input in tool_call.items():
                        UI_TOOLS[tool_name].render(**tool_input)
                st.write(response)
        else:
            st.chat_message(message[0]).write(message[1])


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main layout."""
    st.set_page_config(TITLE, page_icon="📱")
    st.title(TITLE)
    display_history(app_state.chat_history)

    user_input = st.chat_input("Your message")
    if user_input:
        app_state.chat_history.append((USER_LABEL, user_input))
        st.chat_message(USER_LABEL).write(user_input)

        get_response(
            app_state,
            app_state.chat_history,
        )


if not TESTING:
    main()
