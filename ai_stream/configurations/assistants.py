"""Configuration page for assistants."""

import json
from collections import OrderedDict
from typing import Any
import streamlit as st
from openai.types import ResponseFormatJSONObject
from openai.types import ResponseFormatJSONSchema
from openai.types import ResponseFormatText
from openai.types.beta import CodeInterpreterTool
from openai.types.beta import FileSearchTool
from openai.types.beta import FunctionTool
from ai_stream import TESTING
from ai_stream.config import load_config
from ai_stream.db.aws import FunctionsTable
from ai_stream.db.aws import PromptsTable
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


config = load_config()


def new_assistant() -> dict:
    """Return defaults for a new assistant."""
    return {
        "name": "New Assistant",
        "instructions": "You are a helpful assistant.",
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "top_p": 1.0,
        "file_search_enabled": False,
        "code_interpreter_enabled": False,
        "custom_function_enabled": False,
        "function_ids": [],
        "response_format": "text",
        "json_schema": None,
    }


def retrieve_assistant(app_state: AppState, assistant_id: str) -> dict:
    """Retrieve assistant from OpenAI."""
    assert app_state.openai_client
    asst = app_state.openai_client.beta.assistants.retrieve(assistant_id)
    function_ids = [
        val
        for key, val in asst.metadata.items()  # type: ignore[attr-defined]
        if key.startswith("function_")
    ]
    response_format = "text"
    if isinstance(
        response_format,
        ResponseFormatText | ResponseFormatJSONObject | ResponseFormatJSONSchema,
    ):
        response_format = asst.response_format.type
    return {
        "name": asst.name,
        "instructions": asst.instructions,
        "model": asst.model,
        "temperature": asst.temperature,
        "top_p": asst.top_p,
        "file_search_enabled": any(
            isinstance(tool, FileSearchTool) for tool in asst.tools
        ),
        "code_interpreter_enabled": any(
            isinstance(tool, CodeInterpreterTool) for tool in asst.tools
        ),
        "custom_function_enabled": any(
            isinstance(tool, FunctionTool) for tool in asst.tools
        ),
        "function_ids": function_ids,
        "response_format": response_format,
        "json_schema": None,  # TODO
    }


def setup_configuration_widgets(
    app_state: AppState, assistant_id: str, assistant_name: str
) -> dict[str, Any]:
    """Configuration widgets in the sidebar for configuring OpenAI Assistants."""
    if app_state.current_assistant.get("id", "") != assistant_id:
        if assistant_id.startswith("asst_"):
            app_state.current_assistant = retrieve_assistant(app_state, assistant_id)
        else:
            app_state.current_assistant = new_assistant()

    selected_assistant = app_state.current_assistant
    metadata = {}
    # Assistant name
    new_name: str = st.sidebar.text_input(
        "Assistant Name", value=selected_assistant["name"]
    )

    # System instructions
    prompts = app_state.prompts
    prompt_id: str = st.sidebar.selectbox(
        "Select Prompt", options=prompts, format_func=lambda x: prompts[x]
    )
    system_instructions = PromptsTable.get(prompt_id, prompts[prompt_id]).value
    metadata["prompt_id"] = prompt_id

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
    tools = []
    file_search_enabled: bool = st.sidebar.checkbox(
        "Enable File Search", value=selected_assistant["file_search_enabled"]
    )
    if file_search_enabled:
        tools.append({"type": "file_search"})

    code_interpreter_enabled: bool = st.sidebar.checkbox(
        "Enable Code Interpreter", value=selected_assistant["code_interpreter_enabled"]
    )
    if code_interpreter_enabled:
        tools.append({"type": "code_interpreter"})

    # Add input for custom function schema when requested
    custom_function_enabled: bool = st.sidebar.checkbox(
        "Enable Custom Function Schema",
        value=selected_assistant["custom_function_enabled"],
    )

    if custom_function_enabled:
        functions = app_state.functions
        function_ids = st.sidebar.multiselect(
            "Select Function",
            options=functions,
            format_func=lambda x: functions[x],
            default=selected_assistant["function_ids"],
        )
        items = FunctionsTable.batch_get([(id, functions[id]) for id in function_ids])
        tools.extend(
            [
                {"type": "function", "function": schema.value.as_dict()}
                for schema in items
            ]
        )
        metadata.update({f"function_{i}": id for i, id in enumerate(function_ids)})

    # Add options for response format
    st.sidebar.subheader("Response Format")
    resp_format = ["text", "json_object", "json_schema"]
    default_ind = resp_format.index(selected_assistant["response_format"])
    response_format_option: str = st.sidebar.selectbox(
        "Response Format", options=resp_format, index=default_ind
    )

    json_schema: dict[str, Any] | None = None
    if response_format_option == "json_schema":
        json_schema_str: str = st.sidebar.text_area("JSON Schema", value="")
        # Parse the JSON schema
        try:
            json_schema = json.loads(json_schema_str)
            response_format = {"type": "json_schema", "json_schema": json_schema}
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON in JSON Schema")
    else:
        response_format = {"type": response_format_option}

    # Return the configuration as a dictionary
    configuration: dict[str, Any] = {
        "name": new_name,
        "instructions": system_instructions,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "tools": tools,
        "response_format": response_format,
        "metadata": metadata,
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
    st.sidebar.caption(f"ID: {assistant_id}")

    return assistant_id, assistants[assistant_id]


def add_assistant(app_state: AppState) -> None:
    """Add a new assistant."""
    new_id = "tmp_" + create_id()
    app_state.assistants = OrderedDict(
        [(new_id, new_assistant()["name"])] + list(app_state.assistants.items())
    )


def save_assistant(app_state: AppState, assistant_id: str, configuration: dict) -> str:
    """Save or update the given assistant."""
    if assistant_id.startswith("asst_"):  # Update
        assistant = app_state.openai_client.beta.assistants.update(
            assistant_id, **configuration
        )
    else:
        assistant = app_state.openai_client.beta.assistants.create(**configuration)
    # Register to used prompt and functions
    metadata = configuration["metadata"]
    prompt_id = metadata["prompt_id"]
    prompt_name = app_state.prompts[prompt_id]
    item = PromptsTable.get(prompt_id, prompt_name)
    if assistant.id not in item.used_by:
        item.update(actions=[PromptsTable.used_by.set(item.used_by + [assistant.id])])
    for key, val in metadata.items():
        if not key.startswith("function_"):
            continue
        function_name = app_state.functions[val]
        item = FunctionsTable.get(val, function_name)
        if assistant.id not in item.used_by:
            item.update(
                actions=[FunctionsTable.used_by.set(item.used_by + [assistant.id])]
            )
    return assistant.id


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
    st.code(json.dumps(configuration, indent=4), language="json")

    assert app_state.openai_client
    if st.button("Save Assistant"):
        # Save to OpenAI
        assistant_id = save_assistant(app_state, assistant_id, configuration)
        # Save to app_state.assistants
        app_state.assistants[assistant_id] = configuration["name"]
        st.success(f"Assistant {assistant_id} saved!")

    if st.button("Delete Assistant"):
        # Delete from OpenAI
        if not assistant_id.startswith("asst_"):
            st.warning("Not saved yet.")
            st.stop()
        # Deregister to used prompt and functions
        metadata = configuration["metadata"]
        prompt_id = metadata["prompt_id"]
        prompt_name = app_state.prompts[prompt_id]
        item = PromptsTable.get(prompt_id, prompt_name)
        item.update(
            actions=[PromptsTable.used_by.set(item.used_by.remove(assistant_id))]
        )

        for key, val in metadata.items():
            if not key.startswith("function_"):
                continue
            function_name = app_state.functions[val]
            item = FunctionsTable.get(val, function_name)
            item.update(
                actions=[FunctionsTable.used_by.set(item.used_by.remove(assistant_id))]
            )

        app_state.openai_client.beta.assistants.delete(assistant_id)
        # Delete from app_state.assistants
        del app_state.assistants[assistant_id]
        st.success(f"Assistant {assistant_id} deleted.")


if not TESTING:
    main()
