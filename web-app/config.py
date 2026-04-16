"""Configuration values for the Flask web app."""

from pathlib import Path
import os

from dotenv import load_dotenv

ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ROOT_ENV)


class Config:  # pylint: disable=too-few-public-methods
    """Store configuration values loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    TEMPLATES_AUTO_RELOAD = True

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sign_language_db")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "predictions")
    GAME_PROGRESS_COLLECTION = os.getenv("GAME_PROGRESS_COLLECTION", "game_progress")

    DASHBOARD_REFRESH_MS = int(os.getenv("DASHBOARD_REFRESH_MS", "3000"))
    RECENT_LIMIT = int(os.getenv("RECENT_LIMIT", "10"))
