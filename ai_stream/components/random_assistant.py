"""Random assistant."""

import random
from typing import Any
import numpy as np
from ai_stream.components.messages import AssistantMessage
from ai_stream.components.messages import message_registry


def generate_random_response(user_message: str, message_counter: int) -> Any:
    """Generate a random assistant response based on the user message.

    Args:
        user_message: The message provided by the user.
        message_counter: Used for distinguishing widget keys.

    Returns:
        The assistant's message.
    """
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
        return AssistantMessage(content=assistant_message)

    elif response_type == "output_widget":
        possible_output_widgets = [
            {"widget_type": "LineChart", "widget_data": np.random.randn(20, 3).tolist()},
            {"widget_type": "BarChart", "widget_data": np.random.randn(20, 3).tolist()},
            {
                "widget_type": "Image",
                "widget_data": {
                    "url": "https://via.placeholder.com/150",
                    "caption": "A placeholder image",
                },
            },
            {
                "widget_type": "Table",
                "widget_data": {
                    "Column 1": ["A", "B", "C"],
                    "Column 2": [1, 2, 3],
                    "Column 3": [4.5, 5.5, 6.5],
                },
            },
            {
                "widget_type": "Markdown",
                "widget_data": {
                    "content": (
                        "### This is a Markdown header\n\nHere is some **bold** "
                        "text and *italic* text."
                    )
                },
            },
        ]
        selected_widget = random.choice(possible_output_widgets)
        widget_type = selected_widget["widget_type"]
        widget_data = selected_widget["widget_data"]

        # Convert widget_type to class name and retrieve from the registry
        message_class = message_registry.get(widget_type)

        if message_class:
            assistant_output_widget_message = message_class(widget_data=widget_data)
            return assistant_output_widget_message
        else:
            # Handle unknown widget type
            assistant_message = AssistantMessage(
                content="Sorry, I encountered an unknown widget type."
            )
            return assistant_message

    else:  # response_type == "input_widget"
        widget_key = f"widget_{message_counter}"

        possible_widgets = [
            {
                "widget_type": "TextInput",
                "widget_config": {
                    "label": "Assistant asks: Please provide your name:",
                    "key": widget_key,
                },
            },
            {
                "widget_type": "Selectbox",
                "widget_config": {
                    "label": "Assistant asks: Choose your favorite color:",
                    "options": ["Red", "Green", "Blue", "Yellow", "Purple", "Orange"],
                },
            },
            {
                "widget_type": "Slider",
                "widget_config": {
                    "label": "Assistant asks: Rate your experience from 1 to 10:",
                    "min_value": 1,
                    "max_value": 10,
                    "default": 5,
                },
            },
            {
                "widget_type": "Checkbox",
                "widget_config": {"label": "Assistant asks: Do you agree with the terms?"},
            },
            {
                "widget_type": "DateInput",
                "widget_config": {"label": "Assistant asks: Select your birth date:"},
            },
            {
                "widget_type": "TimeInput",
                "widget_config": {"label": "Assistant asks: What time works best for you?"},
            },
            {
                "widget_type": "NumberInput",
                "widget_config": {
                    "label": "Assistant asks: Enter a number:",
                    "min_value": 0,
                    "max_value": 100,
                    "default": 50,
                },
            },
            {
                "widget_type": "TextArea",
                "widget_config": {
                    "label": "Assistant asks: Please describe your issue in detail:"
                },
            },
        ]
        selected_widget = random.choice(possible_widgets)
        widget_type = selected_widget["widget_type"]
        widget_config = selected_widget["widget_config"]

        # Convert widget_type to class name and retrieve from the registry
        message_class = message_registry.get(widget_type)

        if message_class:
            assistant_widget_message = message_class(widget_config=widget_config, key=widget_key)
            return assistant_widget_message
        else:
            # Handle unknown widget type
            assistant_message = AssistantMessage(
                content="Sorry, I encountered an unknown widget type."
            )
            return assistant_message
