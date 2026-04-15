"""MongoDB connection helpers for the Flask web app."""

from pymongo import MongoClient
from flask import current_app, g


def get_client() -> MongoClient:
    """Return a cached MongoDB client for the current app context."""
    if "mongo_client" not in g:
        g.mongo_client = MongoClient(current_app.config["MONGO_URI"])
    return g.mongo_client


def get_db():
    """Return the configured MongoDB database."""
    client = get_client()
    return client[current_app.config["MONGO_DB_NAME"]]


def get_predictions_collection():
    """Return the configured MongoDB predictions collection."""
    db = get_db()
    return db[current_app.config["MONGO_COLLECTION"]]
