"""Configuration page for assistants."""

import json
from collections import OrderedDict
from typing import Any
import streamlit as st
from pynamodb.exceptions import DoesNotExist
from ai_stream import TESTING
from ai_stream.config import load_config
from ai_stream.db.aws import AssistantsTable
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


config = load_config()


def new_assistant() -> dict:
    """Return defaults for a new assistant."""
    return {
        "assistant_name": "New Assistant",
        "system_instructions": "You are a helpful assistant.",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "top_p": 1.0,
        "file_search_enabled": False,
        "code_interpreter_enabled": False,
        "custom_function_enabled": False,
        "function_schema": None,
        "response_format_option": "Text",
        "json_schema": None,
    }


def setup_configuration_widgets(
    app_state: AppState, assistant_id: str, assistant_name: str
) -> dict[str, Any]:
    """Configuration widgets in the sidebar for configuring OpenAI Assistants."""
    if app_state.current_assistant.get("id", "") != assistant_id:
        try:
            item = AssistantsTable.get(assistant_id, assistant_name)
            app_state.current_assistant = item.value.as_dict()
            app_state.current_assistant["id"] = assistant_id
        except DoesNotExist:
            app_state.current_assistant = new_assistant()

    selected_assistant = app_state.current_assistant
    # Assistant name
    new_assistant_name: str = st.sidebar.text_input(
        "Assistant Name", value=selected_assistant["assistant_name"]
    )

    # System instructions
    system_instructions: str = st.sidebar.text_area(
        "System Instructions", value=selected_assistant["system_instructions"]
    )

    # Model selection
    models = list(config.models)
    default_ind = models.index(selected_assistant["model"])
    model: str = st.sidebar.selectbox("Model", options=models, index=default_ind)

    # Temperature
    temperature: float = st.sidebar.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=selected_assistant["temperature"],
    )

    # Top-p
    top_p: float = st.sidebar.slider(
        "Top-p", min_value=0.0, max_value=1.0, value=selected_assistant["top_p"]
    )

    # Add toggles for file search and code interpreter
    st.sidebar.subheader("Tools")
    file_search_enabled: bool = st.sidebar.checkbox(
        "Enable File Search", value=selected_assistant["file_search_enabled"]
    )
    code_interpreter_enabled: bool = st.sidebar.checkbox(
        "Enable Code Interpreter", value=selected_assistant["code_interpreter_enabled"]
    )

    # Add input for custom function schema when requested
    st.sidebar.subheader("Custom Function Schema")
    custom_function_enabled: bool = st.sidebar.checkbox(
        "Enable Custom Function Schema",
        value=selected_assistant["custom_function_enabled"],
    )

    function_schema: dict[str, Any] | None = None
    if custom_function_enabled:
        function_schema_str: str = st.sidebar.text_area(
            "Function Schema (JSON format)", value=""
        )
        # Parse the function schema
        try:
            function_schema = json.loads(function_schema_str)
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON in Function Schema")
            function_schema = None

    # Add options for response format
    st.sidebar.subheader("Response Format")
    resp_format = ["Text", "JSON Object", "JSON Schema"]
    default_ind = resp_format.index(selected_assistant["response_format_option"])
    response_format_option: str = st.sidebar.selectbox(
        "Response Format", options=resp_format, index=default_ind
    )

    json_schema: dict[str, Any] | None = None
    if response_format_option == "JSON Schema":
        json_schema_str: str = st.sidebar.text_area("JSON Schema", value="")
        # Parse the JSON schema
        try:
            json_schema = json.loads(json_schema_str)
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON in JSON Schema")
            json_schema = None

    # Return the configuration as a dictionary
    configuration: dict[str, Any] = {
        "assistant_name": new_assistant_name,
        "system_instructions": system_instructions,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "file_search_enabled": file_search_enabled,
        "code_interpreter_enabled": code_interpreter_enabled,
        "custom_function_enabled": custom_function_enabled,
        "function_schema": function_schema,
        "response_format_option": response_format_option,
        "json_schema": json_schema,
    }
    return configuration


def select_assistant(assistants: dict) -> tuple:
    """Select assistant and return its ID and name."""
    if not assistants:
        st.warning("No assistants yet. Click 'New Assistant' to create one.")
        st.stop()

    assistant_id = st.sidebar.selectbox(
        "Select Assistant", options=assistants, format_func=lambda x: assistants[x]
    )

    return assistant_id, assistants[assistant_id]


def add_assistant(app_state: AppState) -> None:
    """Add a new assistant."""
    new_id = create_id()
    app_state.assistants = OrderedDict(
        [(new_id, new_assistant()["assistant_name"])]
        + list(app_state.assistants.items())
    )


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main function to run the Streamlit app."""
    st.title("OpenAI Assistant Configuration")

    if st.button("New Assistant"):
        add_assistant(app_state)

    assistant_id, assistant_name = select_assistant(app_state.assistants)
    configuration = setup_configuration_widgets(app_state, assistant_id, assistant_name)

    # Display the current configuration for demonstration purposes
    st.subheader("Current Configuration")
    st.json(configuration)


if not TESTING:
    main()
