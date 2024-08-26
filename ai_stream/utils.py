"""Definitions of app specific states."""

from collections.abc import Callable
from functools import wraps
from typing import Any
from streamlit import session_state


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
        self.chat_history: list = []
        """Chat history when talking to chatbot."""


def ensure_app_state(func: Callable) -> Callable:
    """Ensure app_state is initialised and pass it to the decorated function."""

    @wraps(func)
    def wrapper(*args: list, **kwargs: dict) -> Any:
        if "app_state" not in session_state:
            session_state.app_state = AppState()
        return func(session_state.app_state, *args, **kwargs)

    return wrapper
