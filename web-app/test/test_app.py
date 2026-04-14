"""Unit tests for Flask web app routes."""

import pytest
from app import app as flask_app


@pytest.fixture(name="client")
def fixture_client():
    """Create a test client for the Flask app."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


def test_guide_page_status(client):
    """Test if the guide page returns a 200 status code."""
    res = client.get("/guide")
    assert res.status_code == 200
    assert b"Garbage Classification Guide" in res.data


def test_guide_content_categories(client):
    """Test if the guide page contains the 4 main garbage categories."""
    res = client.get("/guide")
    html_content = res.data.decode("utf-8")

    assert "Recyclable" in html_content
    assert "Hazardous" in html_content
    assert "Food / Kitchen" in html_content
    assert "Other / General" in html_content


def test_unknown_route_returns_404(client):
    """Test that an unknown route correctly returns a 404 status."""
    res = client.get("/nonexistent")
    assert res.status_code == 404
