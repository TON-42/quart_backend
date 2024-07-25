"""
This module loads configuration from environment variables.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """
    Config class to load and store environment variables for the application.
    """

    load_dotenv()

    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    TOKEN = os.getenv("BOT_TOKEN", "")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    API_USERNAME = os.getenv("API_USERNAME", "")
    API_PASSWORD = os.getenv("API_PASSWORD", "")

    POSTGRES_USER = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Session related configuration
    SESSION_EXPIRATION_MINUTES = int(os.getenv("SESSION_EXPIRATION_MINUTES", "4"))
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))

    # Debug prints

    if not DATABASE_URL:
        logger.error("No DATABASE_URL found in environment variables")
        raise ValueError("No DATABASE_URL found in environment variables")

    # Debug logs
    logger.info("API_ID: %s", API_ID)
    logger.info("API_HASH: %s", API_HASH)
    logger.info("TOKEN: %s", TOKEN)
    logger.info("JWT_SECRET_KEY: %s", JWT_SECRET_KEY)
    logger.info("API_USERNAME: %s", API_USERNAME)
    logger.info("API_PASSWORD: %s", API_PASSWORD)
    logger.info("POSTGRES_USER: %s", POSTGRES_USER)
    logger.info("POSTGRES_PASSWORD: %s", POSTGRES_PASSWORD)
    logger.info("POSTGRES_DB: %s", POSTGRES_DB)
    logger.info("POSTGRES_PORT: %d", POSTGRES_PORT)
    logger.info("POSTGRES_HOST: %s", POSTGRES_HOST)
    logger.info("DATABASE_URL: %s", DATABASE_URL)
    logger.info("SESSION_EXPIRATION_MINUTES: %d", SESSION_EXPIRATION_MINUTES)
    logger.info("CHECK_INTERVAL_SECONDS: %d", CHECK_INTERVAL_SECONDS)
