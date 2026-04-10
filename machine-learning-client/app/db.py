"""Database helpers for saving practice session data."""

from pymongo import MongoClient

from app.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME


def get_collection():
    """
    Get the MongoDB collection for practice sessions.

    Returns:
        The MongoDB collection object.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    return collection


# for saving
def save_practice_session(
    filename: str,
    transcript: str,
    analysis: dict,
):
    """
    Save a practice session document to MongoDB.

    Args:
        filename: Name of the audio file.
        transcript: Transcript text of the session.
        analysis: Analysis results including word count, wpm,
            filler_words, and total_filler_count.

    Returns:
        The inserted MongoDB document ID.
    """
    collection = get_collection()
    document = {
        "filename": filename,
        "transcript": transcript,
        "word_count": analysis["word_count"],
        "wpm": analysis["wpm"],
        "filler_words": analysis["filler_words"],
        "total_filler_count": analysis["total_filler_count"],
    }

    result = collection.insert_one(document)
    return result.inserted_id
