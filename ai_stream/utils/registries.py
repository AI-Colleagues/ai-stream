"""Page registries."""

from collections import defaultdict
from typing import Any
import streamlit as st
from streamlit.navigation.page import StreamlitPage


class AppPage:
    """Base class for app pages."""

    group: str
    page: StreamlitPage
    weight: float
    widget_defaults: dict[str, Any]


_registry_dict: dict[str, dict] = defaultdict(dict)
page_registry: dict[str, list] = defaultdict(list)


def register_page(cls: type[AppPage]) -> None:
    """Register an AppPage, sorted by weight."""
    _registry_dict[cls.group][cls.weight] = cls.page
    # Keep the group sorted
    page_registry[cls.group] = list(
        dict(sorted(_registry_dict[cls.group].items())).values()
    )


@register_page
class MainPage(AppPage):
    """Main page."""

    group: str = ""
    page: StreamlitPage = st.Page("stream.py", title="AI Stream", icon="📱")
    weight: float = 0


# Configurations
@register_page
class PromptsPage(AppPage):
    """Prompts page."""

    group: str = "Configurations"
    page: StreamlitPage = st.Page(
        "configurations/prompts.py", title="Prompts", icon="📝"
    )
    weight: float = 0


@register_page
class FunctionToolsPage(AppPage):
    """Function tools page."""

    group: str = "Configurations"
    page: StreamlitPage = st.Page(
        "configurations/function_tools.py", title="Function Tools", icon="🛠️"
    )
    weight: float = 1


@register_page
class AssistantsPage(AppPage):
    """Main page."""

    group: str = "Configurations"
    page: StreamlitPage = st.Page(
        "configurations/assistants.py", title="Assistants", icon="🤖"
    )
    weight: float = 2
