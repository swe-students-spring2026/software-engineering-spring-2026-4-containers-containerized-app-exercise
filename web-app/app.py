"""Flask web application for garbage classification system."""
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import tempfile
from inference_sdk import InferenceHTTPClient

load_dotenv()

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
    ml_model_url = os.getenv("ML_MODEL_URL", "https://serverless.roboflow.com")
    ml_model_api_key = os.getenv("ML_MODEL_API_KEY", "")
    image_file = request.files.get("image")
    item = request.form.get("item", "Plastic Bottle")

    client = InferenceHTTPClient(
        api_url=ml_model_url,
        api_key=ml_model_api_key,
    )

    result = {
        "item": item,
        "category": "Unknown",
        "bin": "Unknown",
        "confidence": 0,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "model_error": None,
    }

    def normalize_json(value):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, dict):
            return {k: normalize_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [normalize_json(v) for v in value]
        return value

    def normalize_confidence(value):
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
        if not category_value:
            return "Unknown"
        normalized = str(category_value).lower()
        if "recycl" in normalized or "plastic" in normalized or "paper" in normalized:
            return "Blue"
        if "compost" in normalized or "food" in normalized or "organic" in normalized:
            return "Green"
        if "trash" in normalized or "landfill" in normalized or "other" in normalized:
            return "Gray"
        return "Unknown"

    try:
        if image_file:
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(image_file.filename)[1], delete=False) as temp_file:
                image_file.save(temp_file.name)
                temp_path = temp_file.name

            inference_response = client.infer(temp_path, model_id="garbage-classification-3/2")
            os.unlink(temp_path)
        else:
            inference_response = client.infer(item, model_id="garbage-classification-3/2")

        if hasattr(inference_response, "json"):
            response_data = inference_response.json()
        elif isinstance(inference_response, dict):
            response_data = inference_response
        else:
            response_data = {}

        if isinstance(response_data, dict) and response_data:
            response_data = normalize_json(response_data)
            if "predictions" in response_data and response_data["predictions"]:
                top_prediction = response_data["predictions"][0]
                category_value = top_prediction.get("class") or top_prediction.get("label")
                confidence = normalize_confidence(top_prediction.get("confidence"))
                if category_value:
                    result["category"] = category_value
                if confidence:
                    result["confidence"] = confidence
                result["bin"] = map_bin(result["category"])
            else:
                if "category" in response_data:
                    result["category"] = response_data["category"]
                    result["bin"] = map_bin(result["category"])
                if "confidence" in response_data:
                    result["confidence"] = normalize_confidence(response_data["confidence"])
    except Exception as exc:
        app.logger.warning("Model API request failed: %s", exc)
        result["model_error"] = str(exc)

    db_error = None
    try:
        collection.insert_one(result)
    except PyMongoError as exc:
        db_error = str(exc)
        app.logger.error("Failed to save classification result: %s", exc)

    if db_error:
        result["db_error"] = db_error
        result["saved"] = False
    else:
        result["saved"] = True

    return jsonify(normalize_json(result))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
