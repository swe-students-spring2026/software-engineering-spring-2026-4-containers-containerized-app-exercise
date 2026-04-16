from app.config import (
    MONGO_URI,
    MONGO_DB_NAME,
    MONGO_COLLECTION_NAME,
    AUDIO_FILE,
    SAMPLE_RATE,
    CHANNELS,
)

def test_mongo_uri_default_loaded():
    assert MONGO_URI == "mongodb://mongodb:27017"

def test_mongo_db_name_default_loaded():
    assert MONGO_DB_NAME == "ai_speech_coach"

def test_mongo_collection_name_default_loaded():
    assert MONGO_COLLECTION_NAME == "practice_sessions"

def test_audio_file_default_loaded():
    assert AUDIO_FILE == "sample_audio/test.wav"

def test_sample_rate_default():
    assert SAMPLE_RATE == 44100

def test_channels_default():
    assert CHANNELS == 1