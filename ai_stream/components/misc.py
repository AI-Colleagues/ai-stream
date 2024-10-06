"""Miscellaneous components."""

import streamlit as st


def display_used_by(used_by: list[str]) -> None:
    """Display the assistant IDs that uses this function/prompt. `None` if empty."""
    st.subheader("Used By:")
    if used_by:
        st.markdown(", ".join([f"`{asst}`" for asst in used_by]))
    else:
        st.markdown("`None`")
