"""Configuration page for function tools."""

import json
from collections import OrderedDict
from dataclasses import dataclass
from dataclasses import field
import streamlit as st
from code_editor import code_editor
from ai_stream import TESTING
from ai_stream.db.aws import FunctionsTable
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state


PARAM_TYPES = ["string", "number", "integer", "boolean", "array", "object"]


@dataclass
class FunctionParameter:
    """Data class for a function parameter."""

    name: str = ""
    description: str = ""
    type: str = "string"
    required: bool = True
    enum: list = field(default_factory=list)
    items_type: str = "string"
    type_index: int = 0
    items_type_index: int = 0

    def __post_init__(self) -> None:
        """Initialise indexes of parameter type and item_type."""
        self.type_index = PARAM_TYPES.index(self.type)
        self.items_type_index = PARAM_TYPES.index(self.items_type)


def load_from_json_schema(schema: str | dict) -> dict:
    """Converts a JSON Schema into an OpenAI function dictionary."""
    if isinstance(schema, str):
        schema_dict = json.loads(schema)
    else:
        schema_dict = schema
    # Extract the necessary fields
    function_name = schema_dict.get("name")
    function_description = schema_dict.get("description")
    parameters = schema_dict.get("parameters")
    required = parameters.get("required", [])
    converted_params: dict[str, FunctionParameter] = {}
    for param_name, param in parameters["properties"].items():
        param_id = create_id()
        fields = {
            "name": param_name,
            "description": param["description"],
            "type": param["type"],
            "required": param_name in required,
            "enum": param.get("enum", []),  # For enum values
            "items_type": param.get("items", {}).get("type", "string"),
        }
        converted_params[param_id] = FunctionParameter(**fields)

    # Construct the function dictionary
    function_dict = {
        "name": function_name,
        "description": function_description,
        "parameters": converted_params,
    }

    return function_dict


def load_functions(app_state: AppState) -> None:
    """Load functions from DB."""
    if app_state.function_tools:  # Already loaded
        return
    items = FunctionsTable.scan()
    functions = {item.id: load_from_json_schema(item.value.as_dict()) for item in items}
    app_state.function_tools.update(functions)


def add_function(app_state: AppState) -> None:
    """Add a new function."""
    new_id = create_id()
    new_function = {"name": "New Function", "description": "", "parameters": {}}
    app_state.function_tools = OrderedDict(
        [(new_id, new_function)] + list(app_state.function_tools.items())
    )


def remove_function(app_state: AppState, function_id: str, function_name: str) -> None:
    """Remove the given function."""
    del app_state.function_tools[function_id]
    item = FunctionsTable.get(function_id, function_name)
    item.delete()


def build_json_schema(
    function_name: str, function_description: str, parameters: dict
) -> tuple:
    """Build json schema given the function parameters."""
    required_params = [
        param.name for param in parameters.values() if param.required and param.name
    ]
    properties = {}
    for param in parameters.values():
        if not param.name:
            continue  # Skip parameters without a name
        prop = {"type": param.type, "description": param.description}
        if param.type in ["string", "number", "integer"]:
            if param.enum:
                prop["enum"] = param.enum
        if param.type == "array":
            prop["items"] = {"type": param.items_type}
        properties[param.name] = prop

    parameters = {"type": "object", "properties": properties}
    if required_params:
        parameters["required"] = required_params

    schema = {
        "name": function_name,
        "description": function_description,
        "parameters": parameters,
    }

    return schema, json.dumps(schema, indent=2)


def add_parameter(selected_function: dict) -> None:
    """Add a parameter to the given function."""
    new_id = create_id()
    fields = {
        "name": "",
        "description": "",
        "type": "string",
        "required": True,
        "enum": [],  # For enum values
        "items_type": "string",  # Default item type for arrays
    }
    new_param = FunctionParameter(**fields)  # type: ignore[arg-type]
    selected_function["parameters"][new_id] = new_param


def remove_parameter(selected_function: dict, param_id: str) -> None:
    """Remove a parameter from the given function using its id."""
    del selected_function["parameters"][param_id]


def parameter_input(param: FunctionParameter, param_id: str) -> FunctionParameter:
    """Display the input widgets for the given parameter."""
    new_name = st.text_input("Name", value=param.name, key=f"name_{param_id}")
    new_description = st.text_input(
        "Description",
        value=param.description,
        key=f"description_{param_id}",
    )
    new_type = st.selectbox(
        "Type",
        options=PARAM_TYPES,
        index=param.type_index,
        key=f"type_{param_id}",
    )
    new_required = st.checkbox(
        "Required", value=param.required, key=f"required_{param_id}"
    )
    # For enum
    if new_type in ["string", "number", "integer"]:
        enum_input = st.text_input(
            "Enum values (comma-separated)",
            value=", ".join(param.enum),
            key=f"enum_{param_id}",
        )
        # Convert the comma-separated string to a list
        new_enum = [e.strip() for e in enum_input.split(",")] if enum_input else []
    else:
        new_enum = []
    # For array item type
    if new_type == "array":
        new_items_type = st.selectbox(
            "Item Type",
            options=PARAM_TYPES,
            index=param.items_type_index,
            key=f"items_type_{param_id}",
        )
    else:
        new_items_type = "string"
    return FunctionParameter(
        name=new_name,
        description=new_description,
        type=new_type,
        required=new_required,
        enum=new_enum,
        items_type=new_items_type,
    )


def select_function(app_state: AppState) -> str:
    """Select a function to edit and return its id."""
    load_functions(app_state)

    if not app_state.function_tools:
        st.write("No functions available. Click 'New Function' to create one.")
        st.stop()

    function_id2name = {
        func_id: func["name"] for func_id, func in app_state.function_tools.items()
    }

    function_id = st.sidebar.selectbox(
        "Select Function",
        options=function_id2name,
        format_func=lambda x: function_id2name[x],
        key="function_selectbox",
    )
    st.sidebar.caption(f"ID: {function_id}")

    return function_id


def get_function(app_state: AppState, function_id: str) -> dict:
    """Get the function dict given its ID."""
    stored_function = app_state.function_tools[function_id]
    if st.checkbox("Expert Mode"):
        _, current_schema = build_json_schema(
            stored_function["name"],
            stored_function["description"],
            stored_function["parameters"],
        )
        with st.expander("Load from JSON Schema", expanded=True):
            st.write(
                "Press `Control + Enter` (Windows) or `Command + Enter` (Mac) "
                "to load the changes."
            )
            code = code_editor(current_schema, lang="json", height=200)
            return load_from_json_schema(code["text"] or current_schema)
    else:
        return stored_function


def display_function(selected_function: dict, function_id: str) -> tuple:
    """Display the selected function."""
    new_name = st.text_input(
        "Function Name",
        value=selected_function.get("name", ""),
        key=f"function_name_{function_id}",
    )
    new_description = st.text_area(
        "Function Description",
        value=selected_function.get("description", ""),
        key=f"function_description_{function_id}",
    )

    st.header("Parameters")

    # Button to add a new parameter
    if st.button("Add Parameter"):
        add_parameter(selected_function)

    # Display each parameter
    updated_parameters = {}
    for param_id, param in selected_function["parameters"].items():
        with st.expander(f"Parameter: {param.name or 'Unnamed'}", expanded=True):
            output_param = parameter_input(param, param_id)
            updated_parameters[param_id] = output_param
            # Remove button for the parameter
            if st.button("Remove Parameter", key=f"remove_{param_id}"):
                remove_parameter(selected_function, param_id)
                st.rerun()  # Rerun the app to reflect changes

    return new_name, new_description, updated_parameters


@ensure_app_state
def main(app_state: AppState) -> None:
    """Main layout."""
    st.title("OpenAI Function Schema Builder")

    # Button to add a new function
    if st.button("New Function"):
        add_function(app_state)

    function_id = select_function(app_state)

    # Now get the selected function
    selected_function = get_function(app_state, function_id)

    # Display function

    new_name, new_description, updated_parameters = display_function(
        selected_function, function_id
    )

    # Build the JSON schema using the function
    schema, json_schema = build_json_schema(
        new_name,
        new_description,
        updated_parameters,
    )

    st.header("Generated JSON Schema")

    st.code(json_schema, language="json")

    if st.button("Save Function"):
        item = FunctionsTable(
            id=function_id, name=selected_function["name"], value=schema
        )
        item.save()
        st.success("Saved to DB.")

    # Option to remove the function
    if st.button("Remove Function"):
        remove_function(app_state, function_id, selected_function["name"])
        st.rerun()


if not TESTING:
    main()
