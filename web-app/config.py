import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# pylint: disable=too-few-public-methods
class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DB_NAME = os.getenv("DB_NAME", "fridge_app")

    UPLOAD_FOLDER = BASE_DIR / "uploads"
    RUNTIME_FOLDER = BASE_DIR / "runtime"
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
