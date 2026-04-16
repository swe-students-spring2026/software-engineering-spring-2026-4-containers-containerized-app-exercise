"""Tests for the config module."""

import importlib

from app import config as config_module


def test_config_defaults(monkeypatch):
    """Config should use default values when env vars are missing."""
    monkeypatch.delenv("MONGO_URI", raising=False)
    monkeypatch.delenv("DB_NAME", raising=False)
    monkeypatch.delenv("COLLECTION_NAME", raising=False)
    monkeypatch.delenv("POLL_INTERVAL", raising=False)
    monkeypatch.delenv("PASS_THRESHOLD", raising=False)

    config = importlib.reload(config_module)

    assert config.MONGO_URI == "mongodb://localhost:27017"
    assert config.DB_NAME == "emotion_db"
    assert config.COLLECTION_NAME == "scans"
    assert config.POLL_INTERVAL == 3
    assert config.PASS_THRESHOLD == 60.0


def test_config_reads_environment(monkeypatch):
    """Config should read environment variable overrides."""
    monkeypatch.setenv("MONGO_URI", "mongodb://mongo:27017")
    monkeypatch.setenv("DB_NAME", "actor_db")
    monkeypatch.setenv("COLLECTION_NAME", "attempts")
    monkeypatch.setenv("POLL_INTERVAL", "5")
    monkeypatch.setenv("PASS_THRESHOLD", "75")

    config = importlib.reload(config_module)

    assert config.MONGO_URI == "mongodb://mongo:27017"
    assert config.DB_NAME == "actor_db"
    assert config.COLLECTION_NAME == "attempts"
    assert config.POLL_INTERVAL == 5
    assert config.PASS_THRESHOLD == 75.0
