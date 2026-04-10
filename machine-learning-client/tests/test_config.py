"""Tests for app.config."""

from app.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME


def test_mongo_uri_loaded():
    """Test that MONGO_URI is loaded correctly."""
    assert MONGO_URI == "mongodb://localhost:27017/"


def test_mongo_db_name_loaded():
    """Test that MONGO_DB_NAME is loaded correctly."""
    assert MONGO_DB_NAME == "sleep_pandas"


def test_mongo_collection_name_loaded():
    """Test that MONGO_COLLECTION_NAME is loaded correctly."""
    assert MONGO_COLLECTION_NAME == "practice_sessions"
    