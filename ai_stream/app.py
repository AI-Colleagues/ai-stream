"""Entry script."""

import streamlit as st
from ai_stream import TESTING


def main() -> None:
    """Welcome page."""
    from ai_stream.utils.registries import page_registry

    # Define page and navigation
    pg = st.navigation(page_registry)
    pg.run()


if not TESTING:
    main()
