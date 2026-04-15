"""Tests for the Flask web application."""

from unittest.mock import MagicMock

import app as app_module


def test_app_exists():
    """Test that the Flask app object exists."""
    assert app_module.app is not None


def test_home_route():
    """Test that the home route returns a successful response."""
    mock_collection = MagicMock()
    mock_collection.find.return_value.sort.return_value = []

    app_module.app.config["TESTING"] = True

    original_get_collection = app_module.get_collection
    app_module.get_collection = lambda: mock_collection
    try:
        client = app_module.app.test_client()
        response = client.get("/")
        assert response.status_code == 200
    finally:
        app_module.get_collection = original_get_collection
