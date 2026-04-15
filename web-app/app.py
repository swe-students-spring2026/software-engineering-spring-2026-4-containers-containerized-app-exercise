"""Main Flask application for Bird Detection Dashboard."""

from datetime import datetime
import os
import random
from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://admin:admin123@mongodb:27017/?authSource=admin",
)
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "birdnet_db")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
detections_collection = db["detections"]



@app.route("/")
def home():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/start")
def start():
    """Start listening"""
    print("listening started")
    return {"status": "listening started"}


@app.route("/stop")
def stop():
    """End listening"""
    print("listening stopped")
    return {"status": "listening stopped"}


# @app.route("/detections")
# def detections():
#     """Placeholder detection data (replace with DB later)"""
#     birds = ["Sparrow", "Robin", "Blue Jay", "Cardinal"]
#     fake_data = [
#         {
#             "name": random.choice(birds),
#             "confidence": random.randint(70, 99),
#             "time": datetime.now().strftime("%H:%M:%S"),
#         }
#         for _ in range(5)
#     ]
#     return fake_data
@app.route("/detections")
def detections():
    """Return recent detections from MongoDB."""
    docs = list(
        detections_collection.find({}, {"_id": 0}).sort("created_at", -1).limit(20)
    )

    response_docs = [
        {
            "recording_id": str(doc["recording_id"]) if "recording_id" in doc else None,
            "species_name": doc.get("species_name"),
            "confidence": doc.get("confidence"),
            "created_at": (
                doc["created_at"].isoformat() if "created_at" in doc else None
            ),
        }
        for doc in docs
    ]

    return jsonify(response_docs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
