"""Message classes."""

from abc import ABC
from abc import abstractmethod
import streamlit as st
from ai_stream import ASSISTANT_LABEL
from ai_stream import USER_LABEL
from ai_stream.components.widgets import render_input_widget
from ai_stream.components.widgets import render_output_widget


class Message(ABC):
    """Base message."""

    def __init__(self, role, content):
        """Initialise."""
        self.role = role
        self.content = content

    @abstractmethod
    def render(self):
        """Render the message."""
        pass


class UserMessage(Message):
    """User message."""

    def __init__(self, content):
        """Initialise."""
        super().__init__(USER_LABEL, content)

    def render(self):
        """Render the user message as texts."""
        with st.chat_message(USER_LABEL):
            st.write(self.content)


class AssistantMessage(Message):
    """Assistant message."""

    def __init__(self, content):
        """Initialise."""
        super().__init__(ASSISTANT_LABEL, content)

    def render(self):
        """Render the assistant message as texts."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.content)


class AssistantWidgetMessage(Message):
    """Assistant message as an input widget."""

    def __init__(self, widget_type, widget_config, key):
        """Initialise."""
        super().__init__(ASSISTANT_LABEL, None)
        self.widget_type = widget_type
        self.widget_config = widget_config
        self.key = key
        self.value = None
        self.user_input_provided = False

    def render(self):
        """Display the assistant message as an input widget."""
        with st.chat_message(ASSISTANT_LABEL):
            st.write(self.widget_config["label"])
            # Disable the widget if user input has been provided
            disabled = self.user_input_provided
            self.value, self.user_input_provided = render_input_widget(
                self.widget_type, self.widget_config, self.key, self.value, disabled=disabled
            )


class AssistantOutputWidgetMessage(Message):
    """Assistant message as an output widget."""

    def __init__(self, widget_type, widget_data):
        """Initialise."""
        super().__init__(ASSISTANT_LABEL, None)
        self.widget_type = widget_type
        self.widget_data = widget_data

    def render(self):
        """Display the assistant message as an output widget."""
        with st.chat_message(ASSISTANT_LABEL):
            render_output_widget(self.widget_type, self.widget_data)
