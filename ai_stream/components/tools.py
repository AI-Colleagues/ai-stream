"""Tool related definitions."""

from collections.abc import Callable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_function
from pydantic import BaseModel


TOOLS = {}


class Tool(BaseTool):
    """An abstract class for tools used in AI Stream."""

    args_schema: type[BaseModel] | None = None
    name: str = ""
    description: str = ""


def register_tool(cls: type[Tool]) -> Callable:
    """Register a tool."""
    TOOLS[cls.__name__] = cls
    return cls


def tools_to_openai_functions() -> list[dict]:
    """Convert to OpenAI functions."""
    tools = []
    for tool_cls in TOOLS.values():
        schema_cls_name = f"{tool_cls.__name__}Schema"
        schema_cls = getattr(tool_cls, schema_cls_name)
        tools.append({"type": "function", "function": convert_to_openai_function(schema_cls)})  # type: ignore

    return tools
