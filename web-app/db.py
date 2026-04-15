"""Database connection module."""

import os
from pymongo import MongoClient


def get_db():
    """Establish and return a connection to the MongoDB database."""
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/")  
    client = MongoClient(mongo_uri)
    return client.ai_speech_coach