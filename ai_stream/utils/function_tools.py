"""Utils for function tools."""

import json
from dataclasses import dataclass
from dataclasses import field
from langchain_core.utils.function_calling import convert_to_openai_function
from pydantic import BaseModel
from ai_stream.utils import create_id


NEW_SCHEMA_NAME = "New"
PARAM_TYPES = ["string", "number", "integer", "boolean", "array", "object"]


@dataclass
class FunctionParameter:
    """Data class for a function parameter."""

    name: str = ""
    description: str = ""
    type: str = "string"  # TODO: Support multi-type annotation (anyOf)
    required: bool = True
    enum: list[str] = field(default_factory=list)
    items_type: str = "string"
    type_index: int = 0
    items_type_index: int = 0

    def __post_init__(self) -> None:
        """Initialise indexes of parameter type and item_type."""
        self.type_index = PARAM_TYPES.index(self.type)
        self.items_type_index = PARAM_TYPES.index(self.items_type)


@dataclass
class Function2Display:
    """Function to display."""

    schema_id: str
    schema_name: str = ""
    function_name: str = ""
    description: str = ""
    parameters: dict[str, FunctionParameter] = field(default_factory=dict)
    used_by: list = field(default_factory=list)
    is_new: bool = False

    @classmethod
    def from_openai_function(
        cls, schema_id: str, schema_name: str, schema: str | dict, is_new: bool = False
    ) -> "Function2Display":
        """Convert a JSON Schema into an AI Stream function dictionary."""
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

        return cls(
            schema_id=schema_id,
            schema_name=schema_name,
            function_name=function_name,
            description=function_description,
            parameters=converted_params,
            is_new=is_new,
        )

    @classmethod
    def from_pydantic_model(
        cls, schema_id: str, schema_name: str, schema: type[BaseModel], is_new: bool = True
    ) -> "Function2Display":
        """Load data from a Pydantic Model."""
        schema_dict = convert_to_openai_function(schema)
        return cls.from_openai_function(
            schema_id=schema_id,
            schema_name=schema_name,
            schema=schema_dict,
            is_new=is_new,
        )

    @classmethod
    def new(cls) -> "Function2Display":
        """Create a new function."""
        return cls(schema_id=create_id(), schema_name=NEW_SCHEMA_NAME, is_new=True)
