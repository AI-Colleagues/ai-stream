"""Definition of widgets and rendering."""

import pandas as pd
import streamlit as st


def render_input_widget(widget_type, widget_config, key, current_value, disabled=False):
    """Render an input widget given the config."""
    user_input_provided = False
    value = current_value

    if widget_type == "text_input":
        value = st.text_input(
            label="", value=current_value if current_value else "", key=key, disabled=disabled
        )
        user_input_provided = value != ""
    elif widget_type == "selectbox":
        options = widget_config["options"]
        value = st.selectbox(
            label="",
            options=options,
            index=options.index(current_value) if current_value in options else 0,
            key=key,
            disabled=disabled,
        )
        user_input_provided = True
    elif widget_type == "slider":
        value = st.slider(
            label="",
            min_value=widget_config["min_value"],
            max_value=widget_config["max_value"],
            value=current_value if current_value is not None else widget_config["default"],
            key=key,
            disabled=disabled,
        )
        user_input_provided = True
    elif widget_type == "checkbox":
        value = st.checkbox(
            label="",
            value=current_value if current_value is not None else False,
            key=key,
            disabled=disabled,
        )
        user_input_provided = True
    elif widget_type == "date_input":
        value = st.date_input(
            label="", value=current_value if current_value else None, key=key, disabled=disabled
        )
        user_input_provided = current_value is not None
    elif widget_type == "time_input":
        value = st.time_input(
            label="", value=current_value if current_value else None, key=key, disabled=disabled
        )
        user_input_provided = current_value is not None
    elif widget_type == "number_input":
        value = st.number_input(
            label="",
            min_value=widget_config["min_value"],
            max_value=widget_config["max_value"],
            value=current_value if current_value is not None else widget_config["default"],
            key=key,
            disabled=disabled,
        )
        user_input_provided = True
    elif widget_type == "text_area":
        value = st.text_area(
            label="", value=current_value if current_value else "", key=key, disabled=disabled
        )
        user_input_provided = value != ""
    return value, user_input_provided


def render_output_widget(widget_type, widget_data):
    """Render an output widget given the type and data."""
    if widget_type == "line_chart":
        st.write("Here's a line chart based on random data:")
        chart_data = pd.DataFrame(widget_data)
        st.line_chart(chart_data)
    elif widget_type == "bar_chart":
        st.write("Here's a bar chart based on random data:")
        chart_data = pd.DataFrame(widget_data)
        st.bar_chart(chart_data)
    elif widget_type == "image":
        st.write("Here's an image:")
        st.image(widget_data["url"], caption=widget_data.get("caption", ""))
    elif widget_type == "table":
        st.write("Here's a table of data:")
        table_data = pd.DataFrame(widget_data)
        st.table(table_data)
    elif widget_type == "markdown":
        st.write("Here's some formatted text:")
        st.markdown(widget_data["content"])
