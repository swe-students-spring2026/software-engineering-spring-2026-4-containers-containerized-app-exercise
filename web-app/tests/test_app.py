"""
Unit tests for the Flask web-app dashboard and health check endpoints.
"""

import pytest
from app import app


@pytest.fixture(name="client")
def fixture_client():
    """
    Initializes a Flask test client for use in test cases.
    """
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_route(client):
    """
    Test the index route to ensure it returns a valid health check JSON response.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "web-app"}
