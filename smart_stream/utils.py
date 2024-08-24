"""Definition for app specific states."""

from collections.abc import Callable
from functools import wraps
from typing import Any
from streamlit import session_state


class AppState:
    """A custom session_state to centralise all session state operations.

    When session_state are used, it's easy to lost the track of their
    initialisation place, adding difficulty to maintenance.
    """

    def __init__(self, *args: list, **kwargs: dict):
        """Initialise all session states used in this app."""
        super().__init__(*args, **kwargs)
        # Predefined states
        self.chat_history: list = []
        """Chat history when tesing chatbot."""


def ensure_app_state(func: Callable) -> Callable:
    """Ensure app_state is initialised and pass it to the decorated function."""

    @wraps(func)
    def wrapper(*args: list, **kwargs: dict) -> Any:
        if "app_state" not in session_state:
            session_state.app_state = AppState()
        return func(session_state.app_state, *args, **kwargs)

    return wrapper
