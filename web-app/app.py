"""Flask web application for garbage classification system."""
import os
import tempfile
from datetime import datetime

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from inference_sdk import InferenceHTTPClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

ML_MODEL_URL = os.getenv("ML_MODEL_URL", "https://serverless.roboflow.com")
ML_MODEL_API_KEY = os.getenv("ML_MODEL_API_KEY", "")
ML_MODEL_ID = os.getenv("ML_MODEL_ID", "garbage-classification-3/2")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DB_NAME = os.getenv("DB_NAME", "garbage_classifier")

app = Flask(__name__)

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db["detections"]

model_client = InferenceHTTPClient(
    api_url=ML_MODEL_URL,
    api_key=ML_MODEL_API_KEY,
)


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
    """Convert a model confidence value into an integer percentage."""
    if value is None:
        return 0
    if isinstance(value, str):
        value = value.strip().replace("%", "")
    try:
        conf_float = float(value)
    except (TypeError, ValueError):
        return 0
    if 0 <= conf_float <= 1:
        return int(conf_float * 100)
    if 1 < conf_float <= 100:
        return int(conf_float)
    return 0


def map_bin(category_value):
    """Choose a bin color based on the predicted category label."""
    if not category_value:
        return "Unknown"
    normalized = str(category_value).lower()
    if any(keyword in normalized for keyword in ("recycl", "plastic", "paper")):
        return "Blue"
    if any(keyword in normalized for keyword in ("compost", "food", "organic")):
        return "Green"
    if any(keyword in normalized for keyword in ("trash", "landfill", "other")):
        return "Gray"
    return "Unknown"


def build_result(item):
    """Create a new result record with default classification values."""
    return {
        "item": item,
        "category": "Unknown",
        "bin": "Unknown",
        "confidence": 0,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "model_error": None,
    }


def fetch_model_response(image_file, item):
    """Send the image or item name to the model and return its raw response."""
    if image_file:
        suffix = os.path.splitext(image_file.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            image_file.save(temp_file.name)
            temp_path = temp_file.name
        response = model_client.infer(temp_path, model_id=ML_MODEL_ID)
        os.unlink(temp_path)
    else:
        response = model_client.infer(item, model_id=ML_MODEL_ID)

    if hasattr(response, "json"):
        return response.json()
    if isinstance(response, dict):
        return response
    return {}


def extract_prediction(response_data, result):
    """Extract category, confidence, and bin information from model response."""
    if not isinstance(response_data, dict):
        return
    if response_data.get("predictions"):
        top_prediction = response_data["predictions"][0]
        result["category"] = (
            top_prediction.get("class")
            or top_prediction.get("label")
            or result["category"]
        )
        result["confidence"] = normalize_confidence(top_prediction.get("confidence"))
    else:
        result["category"] = response_data.get("category", result["category"])
        if response_data.get("confidence") is not None:
            result["confidence"] = normalize_confidence(response_data["confidence"])
    result["bin"] = map_bin(result["category"])


@app.route("/")
def index():
    """Render the home page for uploading garbage images."""
    return render_template("index.html")


@app.route("/result")
def show_result():
    """Render a placeholder result page for the given item."""
    item = request.args.get("item", "Unknown Item")
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
    """Render the history page showing recent classification records."""
    records = list(collection.find().sort("timestamp", -1).limit(20))
    for record in records:
        record["_id"] = str(record["_id"])
    return render_template("history.html", records=records)


@app.route("/guide")
def guide():
    """Render the recycling guide page."""
    return render_template("guide.html")


@app.route("/classify", methods=["POST"])
def classify():
    """Handle the classification request, call the model, and save the result."""
    item = request.form.get("item", "Unknown Item").strip()
    image_file = request.files.get("image")
    result = build_result(item)

    try:
        response_data = fetch_model_response(image_file, item)
        extract_prediction(normalize_json(response_data), result)
    except (OSError, ValueError, TypeError) as exc:
        app.logger.warning("Model API request failed: %s", exc)
        result["model_error"] = str(exc)

    try:
        collection.insert_one(normalize_json(result))
        result["saved"] = True
    except PyMongoError as exc:
        app.logger.error("Failed to save classification result: %s", exc)
        result["saved"] = False
        result["db_error"] = str(exc)

    return jsonify(normalize_json(result))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
