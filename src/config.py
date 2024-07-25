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
    print(f"API_ID: {API_ID}")
    print(f"API_HASH: {API_HASH}")
    print(f"TOKEN: {TOKEN}")
    print(f"JWT_SECRET_KEY: {JWT_SECRET_KEY}")
    print(f"API_USERNAME: {API_USERNAME}")
    print(f"API_PASSWORD: {API_PASSWORD}")
    print(f"POSTGRES_USER: {POSTGRES_USER}")
    print(f"POSTGRES_PASSWORD: {POSTGRES_PASSWORD}")
    print(f"POSTGRES_DB: {POSTGRES_DB}")
    print(f"POSTGRES_PORT: {POSTGRES_PORT}")
    print(f"POSTGRES_HOST: {POSTGRES_HOST}")
    print(f"DATABASE_URL: {DATABASE_URL}")
    print(f"SESSION_EXPIRATION_MINUTES: {SESSION_EXPIRATION_MINUTES}")
    print(f"CHECK_INTERVAL_SECONDS: {CHECK_INTERVAL_SECONDS}")
