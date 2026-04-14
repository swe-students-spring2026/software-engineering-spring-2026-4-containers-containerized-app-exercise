from flask import Flask, request, jsonify
import os
import tempfile
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
    item = request.form.get("item")
    image_file = request.files.get("image")

    try:
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
            return jsonify(response.json())
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
