"""Configuration values for machine learning client."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ROOT_ENV)

MODEL_PATH = os.getenv("MODEL_PATH", "data/processed/sign_language_model.pth")

MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "sign_language_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "predictions")
GAME_PROGRESS_COLLECTION = os.getenv("GAME_PROGRESS_COLLECTION", "game_progress")
