from dotenv import load_dotenv
import os


class Config:
    load_dotenv()

    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    TOKEN = os.getenv("BOT_TOKEN")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    API_USERNAME = os.getenv("API_USERNAME")
    API_PASSWORD = os.getenv("API_PASSWORD")
