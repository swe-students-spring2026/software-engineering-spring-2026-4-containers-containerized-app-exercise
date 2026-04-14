"""Flask web application for garbage classification system."""
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DB_NAME = os.getenv("DB_NAME", "garbage_classifier")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["detections"]  # Store classification results


@app.route("/")
def index():
    """Render the home page."""
    return render_template("index.html")


@app.route("/result")
def show_result():
    """
    Display classification result for a given item.

    Retrieves the item name from query parameters and returns
    a placeholder classification result.

    Returns:
        str: Rendered HTML page with classification result.
    """
    item = request.args.get("item", "Unknown Item")
    # Placeholder result data - later replaced with real ML model output
    result_data = {
        "item": item,
        "category": "Recyclable",
        "bin_color": "Blue",
        "bin_emoji": "♻️",
        "confidence": 92,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    }
    return render_template("result.html", result=result_data)


@app.route("/history")
def history():
    """
    Display recent classification history.

    Fetches the latest 20 classification records from MongoDB.

    Returns:
        str: Rendered HTML page with history records.
    """
    # Get latest 20 records from database
    records = list(collection.find().sort("timestamp", -1).limit(20))
    for r in records:
        r["_id"] = str(r["_id"])
    return render_template("history.html", records=records)


@app.route("/guide")
def guide():
    """Render the recycling guide page."""
    return render_template("guide.html")


# API endpoint for future ML integration (upload image)
@app.route("/classify", methods=["POST"])
def classify():
    """
    Classify an item and store the result.

    Accepts JSON input, generates a placeholder classification,
    and stores the result in MongoDB.

    Returns:
        Response: JSON response containing classification result.
    """
    # Placeholder - will connect to ML client later
    data = request.json or {}
    item = data.get("item", "Plastic Bottle")

    result = {
        "item": item,
        "category": "Recyclable",
        "bin": "Blue",
        "confidence": 89,
        "timestamp": datetime.utcnow(),
    }

    # Save to database
    collection.insert_one(result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
