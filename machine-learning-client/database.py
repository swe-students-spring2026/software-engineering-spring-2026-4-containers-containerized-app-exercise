"""Database connection and operations using pymongo."""

import os
from datetime import datetime, timezone
import pymongo


def get_database():
    """Connect to MongoDB and return the database."""
    client = pymongo.MongoClient(os.environ["MONGO_URI"])
    return client[os.environ.get("MONGO_DB_NAME", "garbage_classifier")]


def save_result(collection, image_path, predictions):
    """
    Save inference result metadata to MongoDB.

    Args:
        collection: pymongo collection object
        image_path: path to the image that was analyzed
        predictions: list of prediction dicts from Roboflow
    """
    document = {
        "timestamp": datetime.now(timezone.utc),
        "image_path": image_path,
        "prediction_count": len(predictions),
        "predictions": predictions,
        "classes_detected": list({p["class"] for p in predictions}),
    }
    result = collection.insert_one(document)
    return result.inserted_id
