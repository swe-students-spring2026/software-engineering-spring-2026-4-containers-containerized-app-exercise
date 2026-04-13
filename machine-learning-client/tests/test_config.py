"""Tests for the config module."""

import importlib

from app import config as config_module


def test_config_defaults(monkeypatch):
    """Config should use default values when env vars are missing."""
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("COLLECTION_NAME", raising=False)
    monkeypatch.delenv("POLL_INTERVAL", raising=False)

    config = importlib.reload(config_module)

    assert config.MONGO_URI == "mongodb://localhost:27017"
    assert config.DB_NAME == "emotion_db"
    assert config.COLLECTION_NAME == "scans"
    assert config.POLL_INTERVAL == 3