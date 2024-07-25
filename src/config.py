"""
This module loads configuration from environment variables.
"""

import os
from dotenv import load_dotenv


class Config:
    """
    Config class to load and store environment variables for the application.
    """

    load_dotenv()
    load_dotenv()

    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    TOKEN = os.getenv("BOT_TOKEN", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    API_USERNAME = os.getenv("API_USERNAME")
    API_PASSWORD = os.getenv("API_PASSWORD")

    # Session related configuration
    SESSION_EXPIRATION_MINUTES = int(os.getenv("SESSION_EXPIRATION_MINUTES", "4"))
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
