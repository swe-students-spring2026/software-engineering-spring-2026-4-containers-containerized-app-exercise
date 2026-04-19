"""Unit tests for ML client database helpers."""

import mongomock
import pytest

import db  # pylint: disable=import-error


@pytest.fixture(autouse=True)
def mock_mongo_client(monkeypatch):
    """Mock the MongoClient in db module using mongomock."""
    client = mongomock.MongoClient()
    monkeypatch.setattr(db, "MongoClient", lambda *args, **kwargs: client)
    return client


def test_get_collection():
    """Test get_collection function."""
    collection = db.get_collection("test_col")
    assert collection.name == "test_col"
    assert collection.database.name == db.DB_NAME


def test_save_snapshot():
    """Test save_snapshot function inserts into snapshots collection."""
    snapshot_data = {"emotion": "happy", "confidence": 0.9}

    db.save_snapshot(snapshot_data)

    collection = db.get_collection(db.SNAPSHOTS_COLLECTION)
    inserted = collection.find_one({"emotion": "happy"})
    assert inserted is not None
    assert inserted["confidence"] == 0.9


def test_save_record():
    """Test save_record alias function inserts into snapshots collection."""
    record_data = {"emotion": "sad", "confidence": 0.8}

    db.save_record(record_data)

    collection = db.get_collection(db.SNAPSHOTS_COLLECTION)
    inserted = collection.find_one({"emotion": "sad"})
    assert inserted is not None
    assert inserted["confidence"] == 0.8
