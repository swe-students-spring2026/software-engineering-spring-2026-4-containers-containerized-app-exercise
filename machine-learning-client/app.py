"""ML Client service for garbage classification inference API."""

import os
import tempfile

from flask import Flask, request, jsonify
from inference_sdk import InferenceHTTPClient

app = Flask(__name__)

ML_MODEL_URL = os.getenv("ML_MODEL_URL", "https://serverless.roboflow.com")
ML_MODEL_API_KEY = os.getenv("ML_MODEL_API_KEY", "")
ML_MODEL_ID = os.getenv("ML_MODEL_ID", "garbage-classification-3/2")

model_client = InferenceHTTPClient(
    api_url=ML_MODEL_URL,
    api_key=ML_MODEL_API_KEY,
)


@app.route("/infer", methods=["POST"])
def infer():
    """Run inference on uploaded image or text item."""
    item = request.form.get("item")
    image_file = request.files.get("image")

    temp_path = None

    try:
        # Case 1: image input
        if image_file:
            suffix = os.path.splitext(image_file.filename)[1] or ".jpg"

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                image_file.save(temp_file.name)
                temp_path = temp_file.name

            response = model_client.infer(temp_path, model_id=ML_MODEL_ID)

        # Case 2: text input
        else:
            response = model_client.infer(item, model_id=ML_MODEL_ID)

        # Normalize response
        if hasattr(response, "json"):
            return jsonify(response.json())

        return jsonify(response)

    except Exception as e:  # API boundary safety catch-all
        app.logger.exception("Inference failed")
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure temp file is always cleaned up
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
