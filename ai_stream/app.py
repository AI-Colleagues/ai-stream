"""Entry script."""

import atexit
import os
import streamlit as st
from moto.server import ThreadedMotoServer
from openai import OpenAI
from ai_stream import TESTING
from ai_stream.config import get_logger
from ai_stream.db.aws import PYNAMODB_TABLES
from ai_stream.db.aws import create_tables
from ai_stream.db.aws import dump_data_to_disk
from ai_stream.db.aws import load_data_from_disk
from ai_stream.utils.app_state import AppState
from ai_stream.utils.app_state import ensure_app_state
from ai_stream.utils.registries import page_defaults_registry


logger = get_logger(__name__)


@st.cache_data
def start_moto() -> None:
    """Start moto server."""
    server = ThreadedMotoServer("127.0.0.1", 5001)
    server.start()


@st.cache_resource
def on_startup() -> None:
    """Start up actions."""
    create_tables()
    load_data_from_disk()
    atexit.register(dump_data_to_disk)


def load_tables(app_state: AppState):
    """Load IDs and names from DB."""
    if not app_state.tables_loaded:
        for table_cls in PYNAMODB_TABLES.values():
            items = table_cls.scan(attributes_to_get=["id", "name"])
            items_dict = {item.id: item.name for item in items}
            table_name = table_cls.Meta.table_name
            setattr(app_state, table_name, items_dict)
        app_state.tables_loaded = True

    if not app_state.openai_client:
        return

    # Load assistants
    # TODO: Add pagination in case number of assistants > 100
    for asst in app_state.openai_client.beta.assistants.list(limit=100):
        app_state.assistants[asst.id] = asst.name


@ensure_app_state
def main(app_state: AppState) -> None:
    """Welcome page."""
    from ai_stream.utils.registries import page_registry

    # Define page and navigation
    project_id = st.sidebar.text_input(
        "OpenAI Project ID", type="password", value=os.environ.get("PROJECT_ID", "")
    )
    kwargs = {"project": project_id} if project_id else {}
    api_key = st.sidebar.text_input(
        "OpenAI Key", type="password", value=os.environ.get("OPENAI_API_KEY", "")
    )
    pg = st.navigation(page_registry)

    if api_key:
        client = OpenAI(api_key=api_key, **kwargs)
        app_state.openai_client = client
    # Skip the api_key checking for random_stream
    elif page_defaults_registry[pg._page].skip_api_key:
        pass
    else:
        st.warning("Your OpenAI API key is needed for using this page.")
        st.stop()
    load_tables(app_state)
    pg.run()


if not TESTING:
    start_moto()
    on_startup()
    main()
