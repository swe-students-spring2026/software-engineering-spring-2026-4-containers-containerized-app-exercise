import os
from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient(os.environ["MONGO_URI"])
db = client[os.getenv("MONGO_DB", "mydatabase")]
collection = db[os.getenv("MONGO_COLLECTION", "attention_events")]


@app.route("/")
def home():
    records = list(collection.find())
    print(records)
    return render_template("index.html", records=records)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
