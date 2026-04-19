"""Unit tests for init_db.py script."""

from unittest.mock import patch
import mongomock

import init_db  # pylint: disable=import-error


@patch("init_db.MongoClient")
def test_init_db_main(mock_mongo_client):
    """Test that main() initializes the database correctly."""
    # Use mongomock to simulate MongoDB behavior
    client = mongomock.MongoClient()
    mock_mongo_client.return_value = client

    # Run the init script
    init_db.main()

    # Assert collections are created
    database = client[init_db.DB_NAME]
    collections = database.list_collection_names()

    assert "users" in collections
    assert "sessions" in collections
    assert "snapshots" in collections

    # Assert indexes are created (mongomock has basic index info)
    users_info = database["users"].index_information()
    assert any("username" in str(idx) for idx in users_info.values())

    sessions_info = database["sessions"].index_information()
    assert any("user_id" in str(idx) for idx in sessions_info.values())
    assert any("status" in str(idx) for idx in sessions_info.values())

    snapshots_info = database["snapshots"].index_information()
    assert any("session_id" in str(idx) for idx in snapshots_info.values())
