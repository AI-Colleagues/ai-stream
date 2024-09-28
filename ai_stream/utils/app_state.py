"""Definitions of app specific states."""

import os
from collections.abc import Callable
from functools import wraps
from typing import Any
from openai import OpenAI
from streamlit import session_state
from ai_stream.db.aws import PYNAMODB_TABLES


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
        self.current_function: dict = {}
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
            project_id = os.environ.get("PROJECT_ID", None)
            client = OpenAI(project=project_id)
            app_state.openai_client = client
            # Load IDs and names from DB
            for table_cls in PYNAMODB_TABLES.values():
                items = table_cls.scan(attributes_to_get=["id", "name"])
                items_dict = {item.id: item.name for item in items}
                table_name = table_cls.Meta.table_name
                setattr(app_state, table_name, items_dict)

            # Load assistants
            # TODO: Add pagination in case number of assistants > 100
            for asst in client.beta.assistants.list(limit=100):
                app_state.assistants[asst.id] = asst.name

            session_state.app_state = app_state

        return func(session_state.app_state, *args, **kwargs)

    return wrapper
