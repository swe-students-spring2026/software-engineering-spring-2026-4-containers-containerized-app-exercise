"""Flask web application for garbage classification system."""

import os
from datetime import datetime

import requests
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://ml-client:8000/infer")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DB_NAME = os.getenv("DB_NAME", "garbage_classifier")

app = Flask(__name__)

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db["detections"]


def normalize_json(value):
    """Convert non-JSON-safe values into JSON-safe equivalents."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {k: normalize_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize_json(v) for v in value]
    return value


def normalize_confidence(value):
    """Convert model confidence into integer percentage."""
    if value is None:
        return 0
    if isinstance(value, str):
        value = value.strip().replace("%", "")
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0

    if 0 <= conf <= 1:
        return int(conf * 100)
    if 1 < conf <= 100:
        return int(conf)
    return 0


def map_bin(category_value):
    """Map category to recycling bin color."""
    if not category_value:
        return "Unknown"

    normalized = str(category_value).lower()

    if any(k in normalized for k in ("recycl", "plastic", "paper")):
        return "Blue"
    if any(k in normalized for k in ("compost", "food", "organic")):
        return "Green"
    if any(k in normalized for k in ("trash", "landfill", "other")):
        return "Gray"

    return "Unknown"


def build_result(item):
    """Create default classification result structure."""
    return {
        "item": item,
        "category": "Unknown",
        "bin": "Unknown",
        "confidence": 0,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "model_error": None,
    }


def fetch_model_response(image_file, item):
    """Call ML service and return inference result."""

    try:
        if image_file:
            files = {"image": (image_file.filename, image_file.stream)}
            data = {"item": item}
            res = requests.post(ML_CLIENT_URL, files=files, data=data, timeout=10)
        else:
            res = requests.post(ML_CLIENT_URL, data={"item": item}, timeout=10)

        return res.json()

    except requests.RequestException as e:
        return {"error": str(e)}


def extract_prediction(response_data, result):
    """Extract prediction results from ML response."""
    if not isinstance(response_data, dict):
        return

    if response_data.get("predictions"):
        top = response_data["predictions"][0]
        result["category"] = top.get("class") or top.get("label") or result["category"]
        result["confidence"] = normalize_confidence(top.get("confidence"))
    else:
        result["category"] = response_data.get("category", result["category"])
        if response_data.get("confidence") is not None:
            result["confidence"] = normalize_confidence(response_data["confidence"])

    result["bin"] = map_bin(result["category"])


@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/history")
def history():
    """Show classification history."""
    records = list(collection.find().sort("timestamp", -1).limit(20))
    for r in records:
        r["_id"] = str(r["_id"])
    return render_template("history.html", records=records)


@app.route("/guide")
def guide():
    """Recycling guide page."""
    return render_template("guide.html")


@app.route("/classify", methods=["POST"])
def classify():
    """Run classification and store result."""
    item = request.form.get("item", "Unknown Item").strip()
    image_file = request.files.get("image")

    result = build_result(item)

    try:
        response = fetch_model_response(image_file, item)
        extract_prediction(normalize_json(response), result)
    except (OSError, ValueError, TypeError) as exc:
        app.logger.warning("Model request failed: %s", exc)
        result["model_error"] = str(exc)

    try:
        collection.insert_one(normalize_json(result))
        result["saved"] = True
    except PyMongoError as exc:
        app.logger.error("DB insert failed: %s", exc)
        result["saved"] = False
        result["db_error"] = str(exc)

    return jsonify(normalize_json(result))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
