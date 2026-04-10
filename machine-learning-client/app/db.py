"""Database helpers for saving practice session data."""

from pymongo import MongoClient

from app.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME


def get_collection():
    """
    Get the MongoDB collection for practice sessions.

    Returns:
        The MongoDB collection object.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    return collection


def save_practice_session(session: dict):
    """
    Save a complete practice session document to MongoDB.

    Args:
        session: A dictionary containing the full practice session data.

    Returns:
        The inserted MongoDB document ID.
    """
    if not isinstance(session, dict):
        raise ValueError("session must be a dictionary")

    collection = get_collection()
    result = collection.insert_one(session)
    return result.inserted_id