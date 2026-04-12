"""Configuration for the ML client.

Reads values from environment variables (and a .env file when present).
This file is intentionally safe to include in development; don't commit secrets.
"""
import os
from dotenv import load_dotenv


load_dotenv()

# Roboflow API key (string). Default empty to avoid accidental leakage.
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "")

# MongoDB connection URI. Defaults to localhost for development.
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# Capture interval (seconds)
try:
    CAPTURE_INTERVAL = int(os.environ.get("CAPTURE_INTERVAL", "30"))
except (TypeError, ValueError):
    CAPTURE_INTERVAL = 30

__all__ = ["ROBOFLOW_API_KEY", "MONGO_URI", "CAPTURE_INTERVAL"]
