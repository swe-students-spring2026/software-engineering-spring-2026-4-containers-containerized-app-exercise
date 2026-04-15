"""Configuration values for the machine learning client."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

# get info from .env file
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_speech_coach")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "practice_sessions")

AUDIO_FILE = os.getenv("AUDIO_FILE", "sample_audio/test.wav")


# add a default recorder
SAMPLE_RATE = 44100
CHANNELS = 1
