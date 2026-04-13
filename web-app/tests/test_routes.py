from unittest.mock import patch

import requests


def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MoodMirror" in response.data
    assert b"Live Emotion Camera" in response.data


def test_health_route(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_db_health_route_success(client):
    with patch("app.routes.ping_db", return_value=True):
        response = client.get("/db-health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["database"] == "connected"


def test_db_health_route_failure(client):
    with patch("app.routes.ping_db", side_effect=RuntimeError("db down")):
        response = client.get("/db-health")

    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "db down" in response.json["message"]


def test_analyze_route_missing_image(client):
    response = client.post("/api/analyze", json={"session_id": "abc"})
    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_analyze_route_success(client):
    with patch(
        "app.routes.submit_frame_for_analysis",
        return_value={
            "status": "ok",
            "emotion": "happy",
            "confidence": 0.95,
            "border_color": "yellow",
            "face_detected": True,
            "inserted_id": "123",
        },
    ) as mock_submit:
        response = client.post(
            "/api/analyze",
            json={
                "session_id": "abc",
                "image_b64": "fake-image-data",
            },
        )

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["emotion"] == "happy"
    mock_submit.assert_called_once_with(
        "http://localhost:5001",
        "fake-image-data",
        "abc",
    )


def test_analyze_route_ml_client_request_exception(client):
    with patch(
        "app.routes.submit_frame_for_analysis",
        side_effect=requests.RequestException("ml offline"),
    ):
        response = client.post(
            "/api/analyze",
            json={
                "session_id": "abc",
                "image_b64": "fake-image-data",
            },
        )

    assert response.status_code == 502
    assert response.json["status"] == "error"
    assert "ml offline" in response.json["message"]


def test_analyze_route_unexpected_exception(client):
    with patch(
        "app.routes.submit_frame_for_analysis",
        side_effect=RuntimeError("unexpected"),
    ):
        response = client.post(
            "/api/analyze",
            json={
                "session_id": "abc",
                "image_b64": "fake-image-data",
            },
        )

    assert response.status_code == 500
    assert response.json["status"] == "error"
    assert "unexpected" in response.json["message"]


def test_api_history_route(client):
    fake_records = [
        {"_id": "1", "emotion": "happy"},
        {"_id": "2", "emotion": "sad"},
    ]

    with patch("app.routes.get_recent_predictions", return_value=fake_records):
        response = client.get("/api/history?limit=2")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert len(response.json["records"]) == 2


def test_api_latest_route(client):
    latest = {"_id": "1", "emotion": "neutral"}

    with patch("app.routes.get_latest_prediction", return_value=latest):
        response = client.get("/api/latest")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["latest"] == latest