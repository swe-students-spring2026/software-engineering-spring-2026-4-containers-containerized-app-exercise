"""Configuration values for the Flask web app."""

import os


class Config:  # pylint: disable=too-few-public-methods
    """Store configuration values loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sign_language_db")
    MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "predictions")

    DASHBOARD_REFRESH_MS = int(os.getenv("DASHBOARD_REFRESH_MS", "3000"))
    RECENT_LIMIT = int(os.getenv("RECENT_LIMIT", "10"))
