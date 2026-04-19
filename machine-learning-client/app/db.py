"""Database helpers for the machine-learning client."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.config import Config


_cached_client = None
_cached_client_source = None


def get_client():
    """Create and cache a MongoDB client."""
    global _cached_client, _cached_client_source  # pylint: disable=global-statement

    if _cached_client is None or _cached_client_source is not MongoClient:
        _cached_client = MongoClient(Config.MONGO_URI)
        _cached_client_source = MongoClient

    return _cached_client


def get_collection():
    """Return the predictions collection."""
    client = get_client()
    db = client[Config.MONGO_DB_NAME]
    return db[Config.MONGO_COLLECTION]


def ping_db():
    """Ping MongoDB."""
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except PyMongoError as exc:
        raise RuntimeError("Failed to ping MongoDB") from exc


def insert_prediction(document):
    """Insert a prediction document."""
    try:
        collection = get_collection()
        result = collection.insert_one(document)
        return str(result.inserted_id)
    except PyMongoError as exc:
        raise RuntimeError("Failed to insert prediction") from exc
    