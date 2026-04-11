import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "emotion_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "scans")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "3"))