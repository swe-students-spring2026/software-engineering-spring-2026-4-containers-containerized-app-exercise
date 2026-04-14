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
