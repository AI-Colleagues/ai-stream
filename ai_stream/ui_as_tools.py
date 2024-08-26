"""Tools for rendering UI."""

from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterable
from typing import Any
from typing import Literal
import streamlit as st
from langchain.pydantic_v1 import BaseModel
from langchain.pydantic_v1 import Field
from langchain_core.tools import BaseTool
from streamlit.runtime.uploaded_file_manager import UploadedFile


UI_TOOLS = {}


class StreamTool(BaseTool, ABC):
    """An abstract class for tools used in AI Stream."""

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
                "Array of allowed extensions. ['png', 'jpg'] The default is "
                "None, which means all extensions are allowed."
            )
        )
        accept_multiple_files: bool = Field(
            description=(
                "If True, allows the user to upload multiple files at the same "
                "time, in which case the return value will be a list of files. "
                "Default: False"
            )
        )
        key: str | int = Field(
            description=(
                "An optional string or integer to use as the unique key for "
                "the widget. If this is omitted, a key will be generated for "
                "the widget based on its content. Multiple widgets of the same "
                "type may not share the same key."
            )
        )
        help: str = Field(
            description="A tooltip that gets displayed next to the file uploader."
        )
        # on_change: Callable = Field(
        #     description="An optional callback invoked when this
        # file_uploader's value changes."
        # )  # TODO: pass callback function names and resolve before rendering
        # args: tuple = Field(
        #     description="An optional tuple of args to pass to the callback."
        # )
        # kwargs: dict = Field(
        #     description="An optional dict of kwargs to pass to the callback."
        # )
        disabled: bool = Field(
            description=(
                "An optional boolean, which disables the file uploader if set "
                "to True. The default is False. This argument can only be "
                "supplied by keyword."
            )
        )
        label_visibility: Literal["visible", "hidden", "collapsed"] = Field(
            description=(
                "The visibility of the label. If 'hidden', the label doesn't "
                "show but there is still empty space for it above the widget "
                "(equivalent to label=''). If 'collapsed', both the label and "
                "the space are removed. Default is 'visible'."
            )
        )

    args_schema: type[BaseModel] = FileUploaderSchema
    name: str = "FileUploader"
    description: str = "Tool for generating a Streamlit file_uploader."

    def _run(self, **kwargs: FileUploaderSchema) -> None:
        pass

    @classmethod
    def render(cls, **kwargs: dict) -> list[UploadedFile] | None:
        """Call by frontend to render the UI."""
        return st.file_uploader(**kwargs)  # type: ignore


@register_tool
class DataFrame(StreamTool):
    """Tool for generating a Streamlit dataframe."""

    class DataFrameSchema(BaseModel):
        """DataFrame schema according to Streamlit docs."""

        # Official implementation has a type alias of Data. However, only
        # standard types (including typing types) are supported by LangChain.
        data: Any = Field(
            description=(
                "The data to display. Can be a pandas.DataFrame, "
                "pandas.Series, pandas.Styler, pandas.Index, pyarrow.Table, "
                "numpy.ndarray, pyspark.sql.DataFrame, snowflake.snowpark."
                "dataframe.DataFrame, snowflake.snowpark.table.Table, "
                "Iterable, dict, or None."
            )
        )
        width: int | None = Field(
            default=None,
            description=(
                "Desired width of the dataframe expressed in pixels. If None "
                "(default), Streamlit sets the dataframe width to fit its "
                "contents up to the width of the parent container."
            ),
        )
        height: int | None = Field(
            default=None,
            description=(
                "Desired height of the dataframe expressed in pixels. If None "
                "(default), Streamlit sets the height to show at most ten "
                "rows. Vertical scrolling within the dataframe element is "
                "enabled when the height does not accommodate all rows."
            ),
        )
        use_container_width: bool = Field(
            default=False,
            description=(
                "Whether to override width with the width of the parent "
                "container. If False (default), Streamlit sets the dataframe's "
                "width according to width. If True, Streamlit sets the width "
                "of the dataframe to match the width of the parent container."
            ),
        )
        hide_index: bool | None = Field(
            default=None,
            description=(
                "Whether to hide the index column(s). If None (default), the "
                "visibility of index columns is automatically determined based "
                "on the data."
            ),
        )
        column_order: Iterable[str] | None = Field(
            default=None,
            description=(
                "The ordered list of columns to display. If None (default), "
                "Streamlit displays all columns in the order inherited from "
                "the underlying data structure. If a list, the indicated "
                "columns will display in the order they appear within the "
                "list. Columns may be omitted or repeated within the list."
            ),
        )
        column_config: dict | None = Field(
            default=None,
            description=(
                "Configuration to customize how columns display. If None "
                "(default), columns are styled based on the underlying data "
                "type of each column. Column configuration can modify column "
                "names, visibility, type, width, or format, among other "
                "things. Must be a dictionary where each key is a column name "
                "and the associated value is one of the following: None, a "
                "string, or a column type within st.column_config."
            ),
        )
        key: str | None = Field(
            default=None,
            description=(
                "An optional string to use for giving this element a stable "
                "identity. If None (default), this element's identity will be "
                "determined based on the values of the other parameters. "
                "Additionally, if selections are activated and key is "
                "provided, Streamlit will register the key in Session State to "
                "store the selection state. The selection state is read-only."
            ),
        )
        on_select: str | Callable = Field(
            default="ignore",
            description=(
                "How the dataframe should respond to user selection events. "
                "This controls whether or not the dataframe behaves like an "
                "input widget. Can be one of the following: 'ignore' "
                "(default), 'rerun', or a callable."
            ),
        )
        selection_mode: str | Iterable[str] = Field(
            default="multi-row",
            description=(
                "The types of selections Streamlit should allow. Can be one of "
                "the following: 'multi-row' (default), 'single-row', "
                "'multi-column', 'single-column', or an Iterable of these "
                "options."
            ),
        )

    args_schema: type[BaseModel] = DataFrameSchema
    name: str = "DataFrame"
    description: str = "Tool for generating a Streamlit dataframe."

    def _run(self, **kwargs: DataFrameSchema) -> None:
        pass

    @classmethod
    def render(cls, **kwargs: dict) -> None:
        """Call by frontend to render the UI."""
        st.dataframe(**kwargs)  # type: ignore


def instantiate_ui_tools() -> list[StreamTool]:
    """Instantiate all the registered tools."""
    tools = []
    for tool_cls in UI_TOOLS.values():
        tools.append(tool_cls())  # type: ignore

    return tools
