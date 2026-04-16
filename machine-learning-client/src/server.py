# pylint: disable=no-member
"""Flask API server for realtime frame prediction."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from inference import load_model, predict
from prediction_log import log_prediction
from preprocessing import preprocess_frame

ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ROOT_ENV)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
MODEL = load_model(DEVICE)


def _decode_base64_image(data_url: str) -> np.ndarray:
    """Decode a base64 data URL into an OpenCV BGR image."""
    if "," not in data_url:
        raise ValueError("Invalid data URL format.")

    _, encoded = data_url.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if frame is None:
        raise ValueError("Could not decode image.")

    return frame


def _has_enough_foreground(gray_28: np.ndarray) -> bool:
    """Return True when the processed image likely contains some foreground."""
    foreground_ratio = float(np.mean(gray_28 > 15))
    max_value = int(np.max(gray_28))
    std_value = float(np.std(gray_28))

    return foreground_ratio > 0.015 and max_value > 35 and std_value > 5.0


@app.route("/health", methods=["GET"])
def health() -> tuple[dict[str, str], int]:
    """Return a simple health check response."""
    return {"status": "ok"}, 200


@app.route("/predict-frame", methods=["POST"])
def predict_frame() -> tuple[Any, int]:
    """Receive one image frame, run inference, save result, and return JSON."""
    payload = request.get_json(silent=True)
    if not payload or "image" not in payload:
        return jsonify({"error": "Missing image field."}), 400

    frame_number = payload.get("frame_number")

    try:
        frame = _decode_base64_image(payload["image"])
        _, gray_28, _ = preprocess_frame(frame, invert=False)

        if not _has_enough_foreground(gray_28):
            log_prediction(
                predicted_label="N/A",
                confidence=0.0,
                current_text="",
                source="browser_camera",
                frame_number=frame_number,
            )
            return (
                jsonify(
                    {
                        "predicted_label": "N/A",
                        "confidence": 0.0,
                        "class_index": -1,
                    }
                ),
                200,
            )

        idx, label, confidence = predict(MODEL, gray_28, DEVICE)

        if confidence < 0.60:
            log_prediction(
                predicted_label="N/A",
                confidence=confidence,
                current_text="",
                source="browser_camera",
                frame_number=frame_number,
            )
            return (
                jsonify(
                    {
                        "predicted_label": "N/A",
                        "confidence": round(confidence, 4),
                        "class_index": -1,
                    }
                ),
                200,
            )

        log_prediction(
            predicted_label=label,
            confidence=confidence,
            current_text=label,
            source="browser_camera",
            frame_number=frame_number,
        )

        return (
            jsonify(
                {
                    "predicted_label": label,
                    "confidence": round(confidence, 4),
                    "class_index": idx,
                }
            ),
            200,
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        return jsonify({"error": str(exc)}), 500
