"""Unit tests for Flask web app routes."""

from unittest.mock import patch, MagicMock
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


# test index page


class TestIndex:
    """Tests for GET /"""

    def test_returns_200(self, client):
        """Home page should return 200."""
        res = client.get("/")
        assert res.status_code == 200

    def test_renders_html(self, client):
        """Response should be HTML."""
        res = client.get("/")
        assert b"<!DOCTYPE html>" in res.data or b"<html" in res.data


# test history


# test guide


class TestGuide:
    """Tests for GET /guide"""

    def test_returns_200(self, client):
        """Guide page should return 200."""
        res = client.get("/guide")
        assert res.status_code == 200

    def test_renders_html(self, client):
        """Response should be HTML."""
        res = client.get("/guide")
        assert b"<!DOCTYPE html>" in res.data or b"<html" in res.data


# test no found


class TestNotFound:
    """Test unknown routes."""

    def test_unknown_route_returns_404(self, client):
        """Unknown route should return 404."""
        res = client.get("/nonexistent")
        assert res.status_code == 404


# test classify
