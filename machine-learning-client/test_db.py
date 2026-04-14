from db import speeches_collection

def test_db_connection():
    result = speeches_collection.insert_one({"test": "connection"})
    assert result.inserted_id is not None
    speeches_collection.delete_one({"_id": result.inserted_id})


def test_insert_speech():
    speech = {
        "title": "test speech",
        "filler_word_count": 3,
        "pace_wpm": 120.0,
        "avg_volume_db": -20.0,
        "pitch_variance": 0.5,
        "duration_seconds": 60.0,
        "transcript": "this is a test",
    }
    result = speeches_collection.insert_one(speech)
    assert result.inserted_id is not None
    speeches_collection.delete_one({"_id": result.inserted_id})
