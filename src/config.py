from dotenv import load_dotenv
import os


class Config:
    load_dotenv()
    load_dotenv()

    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")  # Default to an empty string if not provided
    TOKEN = os.getenv("BOT_TOKEN", "")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
    API_USERNAME = os.getenv("API_USERNAME", "")
    API_PASSWORD = os.getenv("API_PASSWORD", "")

    # Session related configuration
    SESSION_EXPIRATION_MINUTES = int(os.getenv("SESSION_EXPIRATION_MINUTES", 4))
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", 60))
