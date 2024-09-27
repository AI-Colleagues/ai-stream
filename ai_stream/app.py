"""Entry script."""

import atexit
import streamlit as st
from ai_stream import TESTING
from ai_stream.config import get_logger
from ai_stream.db.aws import create_tables
from ai_stream.db.aws import dump_data_to_disk
from ai_stream.db.aws import load_data_from_disk


logger = get_logger(__name__)


@st.cache_resource
def on_startup() -> None:
    """Start up actions."""
    create_tables()
    load_data_from_disk()
    atexit.register(dump_data_to_disk)


def main() -> None:
    """Welcome page."""
    from ai_stream.utils.registries import page_registry

    # Define page and navigation
    pg = st.navigation(page_registry)
    pg.run()


if not TESTING:
    on_startup()
    main()
