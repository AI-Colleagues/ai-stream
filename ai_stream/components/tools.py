"""Tool related definitions."""

from collections.abc import Callable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_function
from pydantic import BaseModel
from pynamodb.exceptions import DoesNotExist
from ai_stream.config import get_logger
from ai_stream.db.aws import FunctionsTable


logger = get_logger(__name__)


class Tool(BaseTool):
    """An abstract class for tools used in AI Stream."""

    args_schema: type[BaseModel] | None = None
    name: str = ""
    description: str = ""


TOOLS: dict[str, type[Tool]] = {}


def register_tool(cls: type[Tool]) -> Callable:
    """Register a tool."""
    tool_name = cls.__name__
    TOOLS[tool_name] = cls
    schema_cls = getattr(cls, f"{tool_name}Schema")
    schema = convert_to_openai_function(schema_cls)
    try:
        item = FunctionsTable.get(tool_name)  # A preserved tool uses its name as ID
        if schema != item.value.as_dict():
            item.update(actions=[FunctionsTable.value.set(schema)])
            logger.info(f"Schema for {tool_name} has been updated.")
    except DoesNotExist:
        item = FunctionsTable(id=tool_name, name=tool_name, used_by=[], value=schema)
        item.save()
        logger.info(f"Stored new schema {tool_name}.")

    return cls


def tools_to_openai_functions() -> list[dict]:
    """Convert to OpenAI functions."""
    tools = []
    for tool_cls in TOOLS.values():
        schema_cls_name = f"{tool_cls.__name__}Schema"
        schema_cls = getattr(tool_cls, schema_cls_name)
        tools.append({"type": "function", "function": convert_to_openai_function(schema_cls)})  # type: ignore

    return tools
