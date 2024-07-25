"""
This module loads configuration from environment variables.
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Config:
    """
    Config class to load and store environment variables for the application.
    """

    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    TOKEN = os.getenv("BOT_TOKEN", "")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")

    POSTGRES_USER = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    DEBUG_MODE = os.getenv("DEBUG_MODE") == "True"

    # Session related configuration
    SESSION_EXPIRATION_MINUTES = int(os.getenv("SESSION_EXPIRATION_MINUTES", "4"))
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

    # Debug prints

    if not DATABASE_URL:
        logger.error("No DATABASE_URL found in environment variables")
        raise ValueError("No DATABASE_URL found in environment variables")

    # Debug logs
    @staticmethod
    def log_config():
        """
        Logs the configuration values.
        """
        logger.info("Configuration Loaded:")
        logger.info("API_ID: %s", Config.API_ID)
        logger.info("API_HASH: %s", Config.API_HASH)
        logger.info("TOKEN: %s", Config.TOKEN)
        logger.info("JWT_SECRET_KEY: %s", Config.JWT_SECRET_KEY)
        logger.info("API_ID: %s", Config.API_ID)
        logger.info("API_HASH: %s", Config.API_HASH)
        logger.info("POSTGRES_USER: %s", Config.POSTGRES_USER)
        logger.info("POSTGRES_PASSWORD: %s", Config.POSTGRES_PASSWORD)
        logger.info("POSTGRES_DB: %s", Config.POSTGRES_DB)
        logger.info("POSTGRES_PORT: %s", Config.POSTGRES_PORT)
        logger.info("POSTGRES_HOST: %s", Config.POSTGRES_HOST)
        logger.info("DATABASE_URL: %s", Config.DATABASE_URL)
        logger.info("SESSION_EXPIRATION_MINUTES: %s", Config.SESSION_EXPIRATION_MINUTES)
        logger.info("CHECK_INTERVAL_SECONDS: %s", Config.CHECK_INTERVAL_SECONDS)
