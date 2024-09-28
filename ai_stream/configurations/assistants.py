"""Configuration page for assistants."""

import json
from typing import Any
import streamlit as st
from ai_stream import TESTING
from ai_stream.config import load_config


config = load_config()


def setup_configuration_widgets() -> dict[str, Any]:
    """Configuration widgets in the sidebar for configuring OpenAI Assistants."""
    st.sidebar.header("Configuration")

    # Assistant name
    assistant_name: str = st.sidebar.text_input("Assistant Name", value="Assistant")

    # System instructions
    system_instructions: str = st.sidebar.text_area(
        "System Instructions", value="You are a helpful assistant."
    )

    # Model selection
    model: str = st.sidebar.selectbox("Model", options=list(config.models))

    # Temperature
    temperature: float = st.sidebar.slider(
        "Temperature", min_value=0.0, max_value=1.0, value=0.7
    )

    # Top-p
    top_p: float = st.sidebar.slider("Top-p", min_value=0.0, max_value=1.0, value=1.0)

    # Add toggles for file search and code interpreter
    st.sidebar.subheader("Tools")
    file_search_enabled: bool = st.sidebar.checkbox("Enable File Search")
    code_interpreter_enabled: bool = st.sidebar.checkbox("Enable Code Interpreter")

    # Add input for custom function schema when requested
    st.sidebar.subheader("Custom Function Schema")
    custom_function_enabled: bool = st.sidebar.checkbox("Enable Custom Function Schema")

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
    response_format_option: str = st.sidebar.selectbox(
        "Response Format", options=["Text", "JSON Object", "JSON Schema"]
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
        "assistant_name": assistant_name,
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


def main() -> None:
    """Main function to run the Streamlit app."""
    st.title("🤖 OpenAI Assistant Configuration")
    configuration = setup_configuration_widgets()

    # Display the current configuration for demonstration purposes
    st.subheader("Current Configuration")
    st.json(configuration)


if not TESTING:
    main()
