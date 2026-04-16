"""Unit tests for the Flask application."""

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=too-few-public-methods
# pylint: disable=no-name-in-module
# pylint: disable=import-error
import sys
import os
import pytest
import db
from app import app

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_get_sessions_empty(client, monkeypatch):
    """Test retrieving sessions when the database is empty."""

    class MockCollection:
        """Mock collection for practice_sessions."""

        def find(self, *args, **kwargs):
            """Mock find method."""
            return []

    class MockDB:
        """Mock database configuration."""

        practice_sessions = MockCollection()

    monkeypatch.setattr("app.get_db", MockDB)

    response = client.get("/api/sessions")
    assert response.status_code == 200
    assert response.get_json() == []


def test_trigger_practice(client, monkeypatch):
    """Test the trigger practice endpoint."""

    class MockCollection:
        """Mock collection for commands."""

        def insert_one(self, doc):
            """Mock insert_one method."""

    class MockDB:
        """Mock database configuration."""

        commands = MockCollection()

    monkeypatch.setattr("app.get_db", MockDB)

    response = client.post("/api/trigger-practice")
    assert response.status_code == 202


def test_get_session_details_found(client, monkeypatch):
    """Test retrieving a specific session that exists."""

    class MockCollection:
        """Mock collection for practice_sessions."""

        def find_one(self, *args, **kwargs):
            """Mock find_one method."""
            return {"session_id": "123", "transcript": "test"}

    class MockDB:
        """Mock database configuration."""

        practice_sessions = MockCollection()

    monkeypatch.setattr("app.get_db", MockDB)
    response = client.get("/api/sessions/507f1f77bcf86cd799439011")
    assert response.status_code == 200


def test_get_session_details_not_found(client, monkeypatch):
    """Test retrieving a specific session that does not exist."""

    class MockCollection:
        """Mock collection for practice_sessions."""

        def find_one(self, *args, **kwargs):
            """Mock find_one method."""
            return None

    class MockDB:
        """Mock database configuration."""

        practice_sessions = MockCollection()

    monkeypatch.setattr("app.get_db", MockDB)
    response = client.get("/api/sessions/507f1f77bcf86cd799439012")
    assert response.status_code == 404


def test_get_db(monkeypatch):
    """Test the database connection initialization."""

    class MockMongoClient:
        """Mock MongoClient."""

        def __init__(self, uri):
            self.uri = uri

        @property
        def ai_speech_coach(self):
            """Mock database attribute."""
            return "mocked_db_instance"

    monkeypatch.setattr("db.MongoClient", MockMongoClient)
    database = db.get_db()
    assert database == "mocked_db_instance"
