"""Initialise."""

import os
from dotenv import load_dotenv


load_dotenv()
TESTING = os.environ.get("TESTING", "false").lower() == "true"
LOCAL_AWS = os.environ.get("LOCAL_AWS", "false").lower() == "true"

__author__ = "AI Colleagues"
__email__ = "info@ai-colleagues.com"
__version__ = "0.0.1"
