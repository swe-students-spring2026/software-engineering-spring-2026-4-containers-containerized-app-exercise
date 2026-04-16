"""Tests for app.config."""
# pylint: disable=import-error

from app.config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_NAME,
    AUDIO_FILE,
    SAMPLE_RATE,
    CHANNELS,
)


def test_mongo_uri_default_loaded():
    """Test default Mongo URI."""
    assert MONGO_URI == "mongodb://mongodb:27017"


def test_mongo_db_name_default_loaded():
    """Test default Mongo database name."""
    assert MONGO_DB_NAME == "ai_speech_coach"


def test_mongo_collection_name_default_loaded():
    """Test default Mongo collection name."""
    assert MONGO_COLLECTION_NAME == "practice_sessions"


def test_audio_file_default_loaded():
    """Test default audio file path."""
    assert AUDIO_FILE == "sample_audio/test.wav"


def test_sample_rate_default():
    """Test default sample rate."""
    assert SAMPLE_RATE == 44100


def test_channels_default():
    """Test default channel count."""
    assert CHANNELS == 1
