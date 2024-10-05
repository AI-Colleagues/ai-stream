"""Message classes."""

from abc import ABC
from abc import abstractmethod
from typing import Any
import pandas as pd
import streamlit as st
from ai_stream import ASSISTANT_LABEL
from ai_stream import USER_LABEL


# Message registry to keep track of all message types
message_registry: dict[str, Any] = {}


def register_message(cls):
    """Register message classes."""
    message_registry[cls.__name__] = cls
    return cls


class Message(ABC):
    """Base class for messages."""

    def __init__(self, role: str, content: str | None = None):
        """Initialize the message."""
        self.role = role
        self.content = content

    @abstractmethod
    def render(self) -> None:
        """Render the message."""
        pass


@register_message
class UserMessage(Message):
    """User message."""

    def __init__(self, content: str):
        """Initialize the user message."""
        super().__init__(USER_LABEL, content)

    def render(self) -> None:
        """Render the user message as text."""
        with st.chat_message(USER_LABEL):
            st.write(self.content)


@register_message
class AssistantMessage(Message):
    """Assistant message."""

    def __init__(self, content: str):
        """Initialize the assistant message."""
        super().__init__(ASSISTANT_LABEL, content)

    def render(self) -> None:
        """Render the assistant message as text."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.content)


class InputWidgetMessage(Message):
    """Base class for assistant messages with input widgets."""

    def __init__(self, widget_config: dict[str, Any], key: str):
        """Initialize the input widget message."""
        super().__init__(ASSISTANT_LABEL)
        self.widget_config = widget_config
        self.key = key
        self.value: Any = None
        self.disabled: bool = False
        self.block_chat_input: bool = False

    def disable(self) -> None:
        """Disable input."""
        self.disabled = True

    @abstractmethod
    def render(self) -> None:
        """Render the input widget."""
        pass


@register_message
class TextInputMessage(InputWidgetMessage):
    """Assistant message with a text input widget."""

    def __init__(self, widget_config: dict[str, Any], key: str):
        """Initialise and set block_chat_input to True."""
        super().__init__(widget_config, key)
        self.block_chat_input = True

    def render(self) -> None:
        """Render the text input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.text_input(
                label="",
                value=self.value or "",
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class SelectboxMessage(InputWidgetMessage):
    """Assistant message with a selectbox widget."""

    def render(self) -> None:
        """Render the selectbox widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            options = self.widget_config["options"]
            current_value = self.value if self.value in options else options[0]
            self.value = st.selectbox(
                label="",
                options=options,
                index=options.index(current_value),
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class SliderMessage(InputWidgetMessage):
    """Assistant message with a slider widget."""

    def render(self) -> None:
        """Render the slider widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            default_value = self.widget_config.get("default", self.widget_config["min_value"])
            self.value = st.slider(
                label="",
                min_value=self.widget_config["min_value"],
                max_value=self.widget_config["max_value"],
                value=self.value if self.value is not None else default_value,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class CheckboxMessage(InputWidgetMessage):
    """Assistant message with a checkbox widget."""

    def render(self) -> None:
        """Render the checkbox widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.checkbox(
                label="",
                value=self.value if self.value is not None else False,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class DateInputMessage(InputWidgetMessage):
    """Assistant message with a date input widget."""

    def render(self) -> None:
        """Render the date input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.date_input(
                label="",
                value=self.value or None,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class TimeInputMessage(InputWidgetMessage):
    """Assistant message with a time input widget."""

    def render(self) -> None:
        """Render the time input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.time_input(
                label="",
                value=self.value or None,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class NumberInputMessage(InputWidgetMessage):
    """Assistant message with a number input widget."""

    def render(self) -> None:
        """Render the number input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            default_value = self.widget_config.get("default", self.widget_config["min_value"])
            self.value = st.number_input(
                label="",
                min_value=self.widget_config["min_value"],
                max_value=self.widget_config["max_value"],
                value=self.value if self.value is not None else default_value,
                key=self.key,
                disabled=self.disabled,
            )


@register_message
class TextAreaMessage(InputWidgetMessage):
    """Assistant message with a text area widget."""

    def __init__(self, widget_config: dict[str, Any], key: str):
        """Initialise and set block_chat_input to True."""
        super().__init__(widget_config, key)
        self.block_chat_input = True

    def render(self) -> None:
        """Render the text area widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config.get("label", ""))
            self.value = st.text_area(
                label="",
                value=self.value or "",
                key=self.key,
                disabled=self.disabled,
            )


class OutputWidgetMessage(Message):
    """Base class for assistant messages with output widgets."""

    def __init__(self, widget_data: Any):
        """Initialize the output widget message."""
        super().__init__(ASSISTANT_LABEL)
        self.widget_data = widget_data

    @abstractmethod
    def render(self) -> None:
        """Render the output widget."""
        pass


@register_message
class LineChartMessage(OutputWidgetMessage):
    """Assistant message that displays a line chart."""

    def render(self) -> None:
        """Render the line chart."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's a line chart based on data:")
            chart_data = pd.DataFrame(self.widget_data)
            st.line_chart(chart_data)


@register_message
class BarChartMessage(OutputWidgetMessage):
    """Assistant message that displays a bar chart."""

    def render(self) -> None:
        """Render the bar chart."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's a bar chart based on data:")
            chart_data = pd.DataFrame(self.widget_data)
            st.bar_chart(chart_data)


@register_message
class ImageMessage(OutputWidgetMessage):
    """Assistant message that displays an image."""

    def render(self) -> None:
        """Render the image."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's an image:")
            st.image(
                self.widget_data["url"],
                caption=self.widget_data.get("caption", ""),
            )


@register_message
class TableMessage(OutputWidgetMessage):
    """Assistant message that displays a table."""

    def render(self) -> None:
        """Render the table."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's a table of data:")
            table_data = pd.DataFrame(self.widget_data)
            st.table(table_data)


@register_message
class MarkdownMessage(OutputWidgetMessage):
    """Assistant message that displays markdown content."""

    def render(self) -> None:
        """Render the markdown content."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write("Here's some formatted text:")
            st.markdown(self.widget_data["content"])
