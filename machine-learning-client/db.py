"""Database connection module for the machine learning client."""
from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["speech_rater"]

speeches_collection = db["speeches"]
