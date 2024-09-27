"""Configuration page for function tools."""

import json
import streamlit as st
from ai_stream import TESTING
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


PARAM_TYPES = ["string", "number", "integer", "boolean", "array", "object"]


def add_function(app_state: AppState) -> None:
    """Add a new function."""
    new_id = create_id()
    new_function = {"name": "New Function", "description": "", "parameters": {}}
    app_state.function_tools[new_id] = new_function


def remove_function(app_state: AppState, function_id: str) -> None:
    """Remove the given function."""
    del app_state.function_tools[function_id]


def build_json_schema(
    function_name: str, function_description: str, parameters: dict
) -> dict:
    """Build json schema given the function parameters."""
    required_params = [
        param["name"]
        for param in parameters.values()
        if param["required"] and param["name"]
    ]
    properties = {}
    for param in parameters.values():
        if not param["name"]:
            continue  # Skip parameters without a name
        prop = {"type": param["type"], "description": param["description"]}
        if param["type"] in ["string", "number", "integer"]:
            if param.get("enum"):
                prop["enum"] = param["enum"]
        if param["type"] == "array":
            prop["items"] = {"type": param["items_type"]}
        properties[param["name"]] = prop

    json_schema = {
        "name": function_name,
        "description": function_description,
        "parameters": {"type": "object", "properties": properties},
    }

    if required_params:
        json_schema["parameters"]["required"] = required_params

    return json_schema


def add_parameter(selected_function: dict) -> None:
    """Add a parameter to the given function."""
    new_id = create_id()
    new_param = {
        "name": "",
        "description": "",
        "type": "string",
        "required": True,
        "enum": [],  # For enum values
        "items_type": "string",  # Default item type for arrays
    }
    selected_function["parameters"][new_id] = new_param


def remove_parameter(selected_function: dict, param_id: str) -> None:
    """Remove a parameter from the given function using its id."""
    del selected_function["parameters"][param_id]


def parameter_input(selected_function: dict, param: dict, param_id: str) -> None:
    """Display the input widgets for the given parameter."""
    param["name"] = st.text_input(
        "Name", value=param.get("name", ""), key=f"name_{param_id}"
    )
    param["description"] = st.text_input(
        "Description",
        value=param.get("description", ""),
        key=f"description_{param_id}",
    )
    param["type"] = st.selectbox(
        "Type",
        options=PARAM_TYPES,
        # index=PARAM_TYPES.index(param.get("type", "string")),
        key=f"type_{param_id}",
    )
    param["required"] = st.checkbox(
        "Required", value=param.get("required", True), key=f"required_{param_id}"
    )
    # For enum
    if param["type"] in ["string", "number", "integer"]:
        enum_input = st.text_input(
            "Enum values (comma-separated)",
            value=", ".join(param.get("enum", [])),
            key=f"enum_{param_id}",
        )
        # Convert the comma-separated string to a list
        param["enum"] = [e.strip() for e in enum_input.split(",")] if enum_input else []
    # For array item type
    if param["type"] == "array":
        param["items_type"] = st.selectbox(
            "Item Type",
            options=PARAM_TYPES,
            # index=PARAM_TYPES.index(param.get("items_type", "string")),
            key=f"items_type_{param_id}",
        )
    # Remove button for the parameter
    if st.button("Remove Parameter", key=f"remove_{param_id}"):
        remove_parameter(selected_function, param_id)
        st.rerun()  # Rerun the app to reflect changes


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main layout."""
    st.title("OpenAI Function Schema Builder")

    # Button to add a new function
    if st.button("New Function"):
        add_function(app_state)

    if not app_state.function_tools:
        st.write("No functions available. Click 'New Function' to create one.")
        st.stop()

    function_id2name = {
        func_id: func["name"] for func_id, func in app_state.function_tools.items()
    }

    function_id = st.selectbox(
        "Select Function",
        options=function_id2name,
        format_func=lambda x: function_id2name[x],
        key="function_selectbox",
    )

    # Now get the selected function
    selected_function = app_state.function_tools[function_id]

    # Function Name and Description
    selected_function["name"] = st.text_input(
        "Function Name",
        value=selected_function.get("name", ""),
        key=f"function_name_{function_id}",
    )
    selected_function["description"] = st.text_area(
        "Function Description",
        value=selected_function.get("description", ""),
        key=f"function_description_{function_id}",
    )

    st.header("Parameters")

    # Button to add a new parameter
    if st.button("Add Parameter"):
        add_parameter(selected_function)

    # Display each parameter
    for param_id, param in selected_function["parameters"].items():
        with st.expander(f"Parameter: {param['name'] or 'Unnamed'}", expanded=True):
            parameter_input(selected_function, param, param_id)

    # Build the JSON schema using the function
    json_schema = build_json_schema(
        selected_function["name"],
        selected_function["description"],
        selected_function["parameters"],
    )

    st.header("Generated JSON Schema")

    json_output = json.dumps(json_schema, indent=2)
    st.code(json_output, language="json")

    # Option to remove the function
    if st.button("Remove Function"):
        remove_function(app_state, function_id)
        st.rerun()


if not TESTING:
    main()
