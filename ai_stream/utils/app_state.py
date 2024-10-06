"""Definitions of app specific states."""

from collections.abc import Callable
from functools import wraps
from typing import Any
from openai import OpenAI
from streamlit import session_state
from ai_stream.utils.function_tools import Function2Display


class AppState:
    """A custom session_state to centralise all session state operations.

    `st.session_state` is problematic, e.g., it's easy to lose track of the
    initialisation places of states. This class acts as a proxy to
    `st.session_state`, so that the definition and usage of states are more
    Pythonic and more tractable.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """Initialise all session states used in this app."""
        super().__init__(*args, **kwargs)
        # Predefined states
        self.history: list = []
        """Chat history when talking to chatbot."""
        self.openai_thread_id: str = ""
        """OpenAI Thread ID."""
        self.prompts: dict = {}
        """Prompt IDs and names, for displaying in the selector."""
        self.functions: dict = {}
        """Function IDs and names, for displaying in the selector."""
        self.assistants: dict = {}
        """Assistant IDs and names, for displaying in the selector."""
        self.recent_tool_output: dict = {}
        """The latest tool output if any."""
        self.current_function: Function2Display | None = None
        """Current function being edited."""
        self.current_assistant: dict = {}
        """Current assistant being edited."""
        self.openai_client: OpenAI | None = None
        """OpenAI client."""


def ensure_app_state(func: Callable) -> Callable:
    """Ensure app_state is initialised and pass it to the decorated function."""

    @wraps(func)
    def wrapper(*args: list, **kwargs: dict) -> Any:
        if "app_state" not in session_state:
            app_state = AppState()
            session_state.app_state = app_state

        return func(session_state.app_state, *args, **kwargs)

    return wrapper
