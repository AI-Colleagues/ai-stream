"""Configuration page for function tools."""

import json
from collections import OrderedDict
import streamlit as st
from code_editor import code_editor
from pynamodb.exceptions import DoesNotExist
from ai_stream import TESTING
from ai_stream.components.misc import display_used_by
from ai_stream.components.tools import TOOLS
from ai_stream.db.aws import FunctionsTable
from ai_stream.utils import create_id
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state
from ai_stream.utils.function_tools import PARAM_TYPES
from ai_stream.utils.function_tools import Function2Display
from ai_stream.utils.function_tools import FunctionParameter


def add_function(app_state: AppState) -> None:
    """Add a new function."""
    new_func = Function2Display.new()
    app_state.current_function = new_func
    app_state.functions = OrderedDict(
        [(new_func.schema_id, new_func.schema_name)] + list(app_state.functions.items())
    )


def remove_function(app_state: AppState, schema_id: str) -> None:
    """Remove the given function."""
    del app_state.functions[schema_id]
    item = FunctionsTable.get(schema_id)
    item.delete()


def build_json_schema(
    function_name: str, function_description: str, parameters: dict[str, FunctionParameter]
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


def add_parameter(selected_function: Function2Display) -> None:
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
    selected_function.parameters[new_id] = new_param


def remove_parameter(selected_function: Function2Display, param_id: str) -> None:
    """Remove a parameter from the given function using its id."""
    del selected_function.parameters[param_id]


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
    new_required = st.checkbox("Required", value=param.required, key=f"required_{param_id}")
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


def choose_function(functions: dict) -> tuple:
    """Select a function to edit and return its id."""
    if not functions:
        st.warning("No functions yet. Click 'New Function' to create one.")
        st.stop()

    schema_id = st.sidebar.selectbox(
        "Select Function",
        options=functions,
        format_func=lambda x: functions[x],
        key="function_selectbox",
    )
    st.sidebar.caption(f"ID: {schema_id}")

    return schema_id, functions[schema_id]


def get_function(app_state: AppState, schema_id: str) -> Function2Display:
    """Get the function dict given its ID."""
    if (
        not app_state.current_function or app_state.current_function.schema_id != schema_id
    ):  # Needs reloading
        try:
            item = FunctionsTable.get(schema_id)
        except DoesNotExist:  # schema_id is for a newly created function
            item = None
        if item:
            app_state.current_function = Function2Display.from_openai_function(
                schema_id, item.name, item.value.as_dict()
            )
            app_state.current_function.used_by = item.used_by

        else:
            st.error(f"Error loading function with ID {schema_id}.")

    stored_function = app_state.current_function
    if st.checkbox("Expert Mode"):
        _, current_schema = build_json_schema(
            stored_function.function_name,
            stored_function.description,
            stored_function.parameters,
        )
        with st.expander("Load from JSON Schema", expanded=True):
            st.write(
                "Press `Control + Enter` (Windows) or `Command + Enter` (Mac) "
                "to load the changes."
            )
            code = code_editor(current_schema, lang="json", height=200)
            new_func = Function2Display.from_openai_function(
                schema_id=stored_function.schema_id,
                schema_name=stored_function.schema_name,
                schema=code["text"] or current_schema,
                is_new=False,
            )
            return new_func
    else:
        return stored_function


def display_function(selected_function: Function2Display) -> tuple:
    """Display the selected function."""
    function_names = list(TOOLS.keys())
    schema_id = selected_function.schema_id
    try:
        function_name = selected_function.function_name
        index = function_names.index(function_name)
    except ValueError:
        index = 0
    new_name = st.selectbox(
        "Function Name",
        options=function_names,
        index=index,
        key=f"function_name_{schema_id}",
    )
    if selected_function.is_new:
        schema_cls = getattr(TOOLS[new_name], f"{new_name}Schema")
        new_func = Function2Display.from_pydantic_model(
            schema_id=selected_function.schema_id,
            schema_name=selected_function.schema_name,
            schema=schema_cls,
        )
        selected_function.description = new_func.description
        selected_function.parameters = new_func.parameters
    new_description = st.text_area(
        "Function Description",
        value=selected_function.description,
        key=f"function_description_{schema_id}",
    )

    st.header("Parameters")

    # Button to add a new parameter
    if st.button("Add Parameter"):
        add_parameter(selected_function)

    # Display each parameter
    updated_parameters = {}
    for param_id, param in selected_function.parameters.items():
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
    """App layout."""
    st.title("OpenAI Function Schema Builder")

    # Button to add a new function
    if st.button("New Function"):
        add_function(app_state)

    schema_id, schema_name = choose_function(app_state.functions)

    # Now get the selected function
    selected_function = get_function(app_state, schema_id)
    display_used_by(selected_function.used_by)
    function_name = selected_function.function_name

    # Display function
    new_name, new_description, updated_parameters = display_function(selected_function)

    # Build the JSON schema using the function
    schema, json_schema = build_json_schema(
        new_name,
        new_description,
        updated_parameters,
    )

    st.header("Generated JSON Schema")

    st.code(json_schema, language="json")

    schema_name = st.text_input("Schema Name", value=schema_name)

    if st.button("Save Function", disabled=not schema_name):
        try:
            existing_function = FunctionsTable.get(schema_id)
        except DoesNotExist:
            existing_function = None
        if existing_function:
            existing_function.update(
                actions=[FunctionsTable.value.set(schema), FunctionsTable.name.set(schema_name)]
            )

            if existing_function.used_by:
                for assistant_id in existing_function.used_by:
                    assistant = app_state.openai_client.beta.assistants.retrieve(assistant_id)
                    tools = [
                        tool.to_dict()
                        for tool in assistant.tools
                        if tool.function.name != function_name
                    ]  # Remove old function
                    tools.append({"type": "function", "function": schema})
                    app_state.openai_client.beta.assistants.update(assistant_id, tools=tools)
            st.success(f"Function has been saved with name {new_name} and " f"ID {schema_id}.")
        else:
            item = FunctionsTable(id=schema_id, name=schema_name, used_by=[], value=schema)
            item.save()
            st.success(f"Function has been saved with name {new_name} and " f"ID {schema_id}.")
        app_state.functions[schema_id] = schema_name

    # Option to remove the function
    if st.button("Remove Function"):
        remove_function(app_state, schema_id)
        st.rerun()


if not TESTING:
    main()
