"""Database connection module for the machine learning client."""
import os
from pymongo import MongoClient

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["speech_rater"]

speeches_collection = db["speeches"]
