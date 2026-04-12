from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["emotion_db"]
scans = db["scans"]

for doc in scans.find():
    print(doc)
