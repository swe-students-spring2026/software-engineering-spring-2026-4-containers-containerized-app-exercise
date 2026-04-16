# pylint: disable=duplicate-code
"""Tests for page routes."""

from __future__ import annotations

from app import create_app


def test_index_page():
    """Test the dashboard page."""
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"Live Translation" in response.data
    assert b"Challenge" in response.data
    assert b"Recent Predictions" in response.data


def test_history_page_default(monkeypatch):
    """Test the history page with default query parameters."""
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

    def mock_get_recent_predictions(limit, search_query, sort_order):
        assert limit == 10
        assert search_query == ""
        assert sort_order == "desc"
        return sample

    monkeypatch.setattr(
        "routes.pages.get_recent_predictions",
        mock_get_recent_predictions,
    )

    with app.test_client() as client:
        response = client.get("/history")

    assert response.status_code == 200
    assert b"Prediction History" in response.data
    assert b"P" in response.data
    assert b"X" in response.data
    assert b"browser_camera" in response.data


def test_history_page_with_search_and_sort(monkeypatch):
    """Test the history page with explicit search and sort parameters."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["RECENT_LIMIT"] = 10

    sample = [
        {
            "timestamp": "2026-04-16T01:08:10.641000",
            "predicted_label": "X",
            "confidence": 0.573,
            "current_text": "X",
            "source": "browser_camera",
            "frame_number": 63,
        }
    ]

    def mock_get_recent_predictions(limit, search_query, sort_order):
        assert limit == 10
        assert search_query == "X"
        assert sort_order == "asc"
        return sample

    monkeypatch.setattr(
        "routes.pages.get_recent_predictions",
        mock_get_recent_predictions,
    )

    with app.test_client() as client:
        response = client.get("/history?search=X&sort=asc")

    assert response.status_code == 200
    assert b"Prediction History" in response.data
    assert b"X" in response.data


def test_history_page_invalid_sort_falls_back_to_desc(monkeypatch):
    """Test invalid sort input falls back to desc."""
    app = create_app()
    app.config["TESTING"] = True
    app.config["RECENT_LIMIT"] = 10

    def mock_get_recent_predictions(limit, search_query, sort_order):
        assert limit == 10
        assert search_query == ""
        assert sort_order == "desc"
        return []

    monkeypatch.setattr(
        "routes.pages.get_recent_predictions",
        mock_get_recent_predictions,
    )

    with app.test_client() as client:
        response = client.get("/history?sort=weird")

    assert response.status_code == 200
    assert b"No prediction history available yet." in response.data
