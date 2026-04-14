import io
import os
import pytest
from unittest.mock import MagicMock, patch

import app  # your Flask app file


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


# ---------------------------
# Mock inference response
# ---------------------------
class MockResponse:
    def json(self):
        return {
            "predictions": [
                {
                    "class": "plastic",
                    "confidence": 0.92
                }
            ]
        }


# ---------------------------
# Test: text input inference
# ---------------------------
@patch("app.model_client")
def test_infer_text(mock_model, client):
    mock_model.infer.return_value = MockResponse()

    response = client.post("/infer", data={"item": "plastic bottle"})

    assert response.status_code == 200
    data = response.get_json()

    assert "predictions" in data
    mock_model.infer.assert_called_once()


# ---------------------------
# Test: image upload inference
# ---------------------------
@patch("app.model_client")
def test_infer_image(mock_model, client):
    mock_model.infer.return_value = MockResponse()

    image = (io.BytesIO(b"fake image data"), "test.jpg")

    response = client.post(
        "/infer",
        data={
            "item": "plastic bottle",
            "image": image
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    data = response.get_json()

    assert "predictions" in data
    mock_model.infer.assert_called_once()


# ---------------------------
# Test: inference failure handling
# ---------------------------
@patch("app.model_client")
def test_infer_failure(mock_model, client):
    mock_model.infer.side_effect = Exception("model error")

    response = client.post("/infer", data={"item": "plastic bottle"})

    assert response.status_code == 500
    data = response.get_json()

    assert "error" in data
    assert data["error"] == "model error"