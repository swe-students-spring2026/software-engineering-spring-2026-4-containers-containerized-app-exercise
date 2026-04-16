# pylint: disable=duplicate-code
"""Tests for API routes."""

from __future__ import annotations

from app import create_app


def test_health_route():
    """Test the health endpoint."""
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_latest_route_with_data(monkeypatch):
    """Test the latest endpoint when data exists."""
    app = create_app()
    app.config["TESTING"] = True

    sample = {
        "timestamp": "2026-04-16T01:08:11.437000",
        "predicted_label": "P",
        "confidence": 1.0,
        "current_text": "P",
        "source": "browser_camera",
        "frame_number": 64,
    }

    def mock_get_latest_prediction():
        return sample

    monkeypatch.setattr(
        "routes.api.get_latest_prediction",
        mock_get_latest_prediction,
    )

    with app.test_client() as client:
        response = client.get("/api/latest")

    assert response.status_code == 200
    assert response.get_json() == sample


def test_latest_route_without_data(monkeypatch):
    """Test the latest endpoint when no data exists."""
    app = create_app()
    app.config["TESTING"] = True

    def mock_get_latest_prediction():
        return None

    monkeypatch.setattr(
        "routes.api.get_latest_prediction",
        mock_get_latest_prediction,
    )

    with app.test_client() as client:
        response = client.get("/api/latest")

    assert response.status_code == 200
    assert response.get_json() == {
        "timestamp": None,
        "predicted_label": "N/A",
        "confidence": 0.0,
        "current_text": "",
        "source": "",
        "frame_number": None,
    }


def test_recent_route(monkeypatch):
    """Test the recent endpoint."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["RECENT_LIMIT"] = 10

    sample = [
        {
            "timestamp": "2026-04-16T01:08:11.437000",
            "predicted_label": "P",
            "confidence": 1.0,
            "current_text": "P",
            "source": "browser_camera",
            "frame_number": 64,
        },
        {
            "timestamp": "2026-04-16T01:08:10.641000",
            "predicted_label": "X",
            "confidence": 0.573,
            "current_text": "X",
            "source": "browser_camera",
            "frame_number": 63,
        },
    ]

    def mock_get_recent_predictions(limit):
        assert limit == 10
        return sample

    monkeypatch.setattr(
        "routes.api.get_recent_predictions",
        mock_get_recent_predictions,
    )

    with app.test_client() as client:
        response = client.get("/api/recent")

    assert response.status_code == 200
    assert response.get_json() == sample


def test_stats_route(monkeypatch):
    """Test the stats endpoint."""
    app = create_app()
    app.config["TESTING"] = True

    sample = {
        "total_predictions": 2,
        "average_confidence": 0.786,
        "top_label": "P",
        "label_counts": {"P": 1, "X": 1},
    }

    def mock_get_prediction_stats(limit):
        assert limit == 100
        return sample

    monkeypatch.setattr(
        "routes.api.get_prediction_stats",
        mock_get_prediction_stats,
    )

    with app.test_client() as client:
        response = client.get("/api/stats")

    assert response.status_code == 200
    assert response.get_json() == sample
