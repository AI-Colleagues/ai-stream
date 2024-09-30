"""Random assistant."""

import random
import numpy as np
from ai_stream.components.messages import AssistantMessage
from ai_stream.components.messages import AssistantOutputWidgetMessage
from ai_stream.components.messages import AssistantWidgetMessage


def generate_random_response(user_message, widget_counter):
    """Get a random response."""
    response_type = random.choice(["input_widget", "output", "output_widget"])

    if response_type == "output":
        possible_messages = [
            f"Thanks for sharing: {user_message}",
            "Could you elaborate on that?",
            "Interesting point!",
            "I appreciate your input.",
            "Let's discuss further.",
            "That's a great question.",
            "I see. Tell me more.",
            f"You said: {user_message}. Let's explore that.",
            "What makes you say that?",
            "How does that make you feel?",
        ]
        assistant_message = random.choice(possible_messages)
        return AssistantMessage(assistant_message), widget_counter
    elif response_type == "output_widget":
        possible_output_widgets = [
            {"widget_type": "line_chart", "widget_data": np.random.randn(20, 3).tolist()},
            {"widget_type": "bar_chart", "widget_data": np.random.randn(20, 3).tolist()},
            {
                "widget_type": "image",
                "widget_data": {
                    "url": "https://via.placeholder.com/150",
                    "caption": "A placeholder image",
                },
            },
            {
                "widget_type": "table",
                "widget_data": {
                    "Column 1": ["A", "B", "C"],
                    "Column 2": [1, 2, 3],
                    "Column 3": [4.5, 5.5, 6.5],
                },
            },
            {
                "widget_type": "markdown",
                "widget_data": {
                    "content": (
                        "### This is a Markdown header\n\nHere is some **bold "
                        "text** and *italic text*."
                    )
                },
            },
        ]
        selected_widget = random.choice(possible_output_widgets)
        assistant_output_widget_message = AssistantOutputWidgetMessage(
            selected_widget["widget_type"], selected_widget["widget_data"]
        )
        return assistant_output_widget_message, widget_counter
    else:
        widget_counter += 1
        widget_key = f"widget_{widget_counter}"

        possible_widgets = [
            {
                "widget_type": "text_input",
                "widget_config": {"label": "Assistant asks: Please provide your name:"},
            },
            {
                "widget_type": "selectbox",
                "widget_config": {
                    "label": "Assistant asks: Choose your favorite color:",
                    "options": ["Red", "Green", "Blue", "Yellow", "Purple", "Orange"],
                },
            },
            {
                "widget_type": "slider",
                "widget_config": {
                    "label": "Assistant asks: Rate your experience from 1 to 10:",
                    "min_value": 1,
                    "max_value": 10,
                    "default": 5,
                },
            },
            {
                "widget_type": "checkbox",
                "widget_config": {"label": "Assistant asks: Do you agree with the terms?"},
            },
            {
                "widget_type": "date_input",
                "widget_config": {"label": "Assistant asks: Select your birth date:"},
            },
            {
                "widget_type": "time_input",
                "widget_config": {"label": "Assistant asks: What time works best for you?"},
            },
            {
                "widget_type": "number_input",
                "widget_config": {
                    "label": "Assistant asks: Enter a number:",
                    "min_value": 0,
                    "max_value": 100,
                    "default": 50,
                },
            },
            {
                "widget_type": "text_area",
                "widget_config": {
                    "label": "Assistant asks: Please describe your issue in detail:"
                },
            },
        ]
        selected_widget = random.choice(possible_widgets)
        assistant_widget_message = AssistantWidgetMessage(
            selected_widget["widget_type"], selected_widget["widget_config"], widget_key
        )
        return assistant_widget_message, widget_counter
