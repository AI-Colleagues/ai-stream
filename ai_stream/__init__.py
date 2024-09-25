"""Initialise."""

import os
from dotenv import load_dotenv


load_dotenv()
TESTING = int(os.environ.get("TESTING", "0"))

__author__ = "AI Colleagues"
__email__ = "info@ai-colleagues.com"
__version__ = "0.0.1"
