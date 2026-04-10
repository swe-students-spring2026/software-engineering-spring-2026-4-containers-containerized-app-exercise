from pymongo import MongoClient
from app.config import MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME


def get_collection():
    client     = MongoClient(MONGO_URI)
    db         = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]
    return collection

# for saving
def save_practice_session(
    filename          : str,
    transcript        : str,
    word_count        : int,
    wpm               : float,
    filler_words      : dict,
    total_filler_count: int,
):
    collection = get_collection()
    document   = {
        "filename"          : filename,
        "transcript"        : transcript,
        "word_count"        : word_count,
        "wpm"               : wpm,
        "filler_words"      : filler_words,
        "total_filler_count": total_filler_count,
    }

    result = collection.insert_one(document)
    return result.inserted_id