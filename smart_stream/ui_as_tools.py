"""Tools for rendering UI."""

from abc import ABC
from abc import abstractmethod
from typing import Literal
import streamlit as st
from langchain.pydantic_v1 import BaseModel
from langchain.pydantic_v1 import Field
from langchain_core.tools import BaseTool


UI_TOOLS = {}


class StreamTool(BaseTool, ABC):
    """An abstract class for tools used in Smart Stream."""

    @classmethod
    @abstractmethod
    def render(cls, **kwargs: dict) -> None:
        """The actual rendering action."""


def register_tool(cls: type[StreamTool]) -> None:
    """Register a tool."""
    UI_TOOLS[cls.__name__] = cls


@register_tool
class FileUploader(StreamTool):
    """Tool for generating a Streamlit file_uploader."""

    class FileUploaderSchema(BaseModel):
        """Schema according to Streamlit docs."""

        label: str = Field(
            description=(
                "A short label explaining to the user what this file uploader "
                "is for. The label can optionally contain GitHub-flavored "
                "Markdown of the following types: Bold, Italics, "
                "Strikethroughs, Inline Code, and Links."
            )
        )
        type: str | list[str] | None = Field(
            description=(
                "Array of allowed extensions. ['png', 'jpg'] The default is None, "
                "which means all extensions are allowed."
            )
        )
        accept_multiple_files: bool = Field(
            description=(
                "If True, allows the user to upload multiple files at the same time, "
                "in which case the return value will be a list of files. Default: False"
            )
        )
        key: str | int = Field(
            description=(
                "An optional string or integer to use as the unique key for the widget. "
                "If this is omitted, a key will be generated for the widget based on its content. "
                "Multiple widgets of the same type may not share the same key."
            )
        )
        help: str = Field(description="A tooltip that gets displayed next to the file uploader.")
        # on_change: Callable = Field(
        #     description="An optional callback invoked when this file_uploader's value changes."
        # )  # TODO: pass callback function names and resolve before rendering
        # args: tuple = Field(
        #     description="An optional tuple of args to pass to the callback."
        # )
        # kwargs: dict = Field(
        #     description="An optional dict of kwargs to pass to the callback."
        # )
        disabled: bool = Field(
            description=(
                "An optional boolean, which disables the file uploader if set to True. "
                "The default is False. This argument can only be supplied by keyword."
            )
        )
        label_visibility: Literal["visible", "hidden", "collapsed"] = Field(
            description=(
                "The visibility of the label. If 'hidden', the label doesn't show but there is "
                "still empty space for it above the widget (equivalent to label=''). "
                "If 'collapsed', both the label and the space are removed. Default is 'visible'."
            )
        )

    args_schema: type[BaseModel] = FileUploaderSchema
    name: str = "FileUploader"
    description: str = "Tool for generating a Streamlit file_uploader."

    def _run(self, **kwargs: FileUploaderSchema) -> None:
        pass

    @classmethod
    def render(cls, **kwargs: dict) -> None:
        """Call by frontend to render the UI."""
        st.file_uploader(**kwargs)  # type: ignore


def instantiate_ui_tools() -> list[StreamTool]:
    """Instantiate all the registered tools."""
    tools = []
    for tool_cls in UI_TOOLS.values():
        tools.append(tool_cls())  # type: ignore

    return tools
