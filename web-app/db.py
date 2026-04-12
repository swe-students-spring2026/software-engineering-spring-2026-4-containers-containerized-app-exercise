"""Database connection module."""

import os
from pymongo import MongoClient


def get_db():
    """Establish and return a connection to the MongoDB database."""
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    return client.speech_coach_db
