"""Unit tests for the Flask web application."""
# pylint: disable=redefined-outer-name, import-error
import pytest
from app import create_app


@pytest.fixture
def client():
    """
    Create and yield Flask app
    """
    app = create_app()
    app.testing = True  # necessary for assertions to work correctly
    with app.test_client() as client:
        yield client


def test_home_page_loads(client):
    """GET / returns 200"""
    response = client.get("/")
    assert response.status_code == 200


def test_filter_by_emotion(client):
    """GET /?emotion=happy returns 200 and contains happy"""
    response = client.get("/?emotion=happy")
    assert response.status_code == 200
    assert b"happy" in response.data.lower()


def test_filter_no_results(client):
    """GET /?emotion=fearful returns 200 even with no matching scans"""
    response = client.get("/?emotion=fearful")
    assert response.status_code == 200


def test_home_page_dummy_data(client):
    """Force the app to use dummy data by setting the DB connection to None"""
    client.application.db = None
    response = client.get("/")
    assert response.status_code == 200
    assert b"surprised" in response.data.lower()


def test_practice_page_loads(client):
    """GET /practice returns 200"""
    response = client.get("/practice")
    assert response.status_code == 200


def test_dummy_data_with_filter(client):
    """Test that the dummy data block correctly filters by emotion"""
    client.application.db = None
    response = client.get("/?emotion=sad")
    assert response.status_code == 200
    assert b"sad" in response.data.lower()


def test_debug_route_no_db(client):
    """GET /debug returns an error JSON when the DB is not connected"""
    client.application.db = None
    response = client.get("/debug")
    assert response.status_code == 200
    assert b"error" in response.data.lower()
