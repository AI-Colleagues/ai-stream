"""Tool related definitions."""

from collections.abc import Callable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_function


class StreamTool(BaseTool):
    """An abstract class for tools used in AI Stream."""

    pass


UI_TOOLS = {}


def register_tool(cls: type[StreamTool]) -> Callable:
    """Register a tool."""
    UI_TOOLS[cls.__name__] = cls
    return cls


def instantiate_ui_tools() -> list[StreamTool]:
    """Instantiate all the registered tools."""
    tools = []
    for tool_cls in UI_TOOLS.values():
        tools.append(tool_cls())  # type: ignore

    return tools


def tools_to_openai_functions() -> list[dict]:
    """Convert to OpenAI functions."""
    tools = []
    for tool_cls in UI_TOOLS.values():
        schema_cls_name = f"{tool_cls.__name__}Schema"
        schema_cls = getattr(tool_cls, schema_cls_name)
        tools.append({"type": "function", "function": convert_to_openai_function(schema_cls)})  # type: ignore

    return tools
