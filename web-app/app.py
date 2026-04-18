import os
import pymongo
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
    """
    Application factory to create and configure the Flask app.
    """
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME", "emotion_db") 
    collection_name = os.getenv('MONGO_COLLECTION', 'scans')

    app.db = None
    app.collection_name = collection_name
    ''''change to app.db = connection[actual name] '''
    try:
        connection = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        connection.server_info()  # Force connection check immediately
        app.db = connection[db_name]
    except Exception as exc:
        print(f"Failed to connect to MongoDB: {exc}")

    @app.route("/debug")
    def debug():
        if app.db is None:
            return {"error": "no db"}

        scans = list(app.db["scans"].find())

        for scan in scans:
            scan["_id"] = str(scan["_id"])

        return jsonify(scans)
    
    @app.route("/")
    def home():
        """
        Main dashboard route.
        Returns dummy data if MongoDB is not connected.
        """
        emotion_filter = request.args.get("emotion", "all")

        emotions = ["happy", "sad", "angry", "surprised", "neutral", "disgusted", "fearful", "depressed"]

        if app.db is not None:
            query = {}
            if emotion_filter != "all":
                query["emotion"] = emotion_filter
            activities = list(app.db.analysis.find(query).limit(50))
            all_scans = list(app.db.analysis.find())
            emotion_counts = {e: 0 for e in emotions}
            for scan in all_scans:
                e = scan.get("emotion", "").lower()
                if e in emotion_counts:
                    emotion_counts[e] += 1
        else:
            activities = [
                {"emotion": "happy", "confidence": 0.92, "timestamp": "2026-04-14 10:00"},
                {"emotion": "sad", "confidence": 0.78, "timestamp": "2026-04-14 10:05"},
                {"emotion": "angry", "confidence": 0.85, "timestamp": "2026-04-14 10:10"},
                {"emotion": "neutral", "confidence": 0.60, "timestamp": "2026-04-14 10:15"},
                {"emotion": "happy", "confidence": 0.88, "timestamp": "2026-04-14 10:20"},
                {"emotion": "surprised", "confidence": 0.73, "timestamp": "2026-04-13 10:25"},
                {"emotion": "depressed", "confidence": 0.40, "timestamp": "2026-04-13 10:25"},
            ]
            if emotion_filter != "all":
                activities = [a for a in activities if a["emotion"] == emotion_filter]
            emotion_counts = {e: 0 for e in emotions}
            all_dummy = [
                "happy", "sad", "angry", "neutral", "happy", "surprised", "depressed"
            ]
            for e in all_dummy:
                if e in emotion_counts:
                    emotion_counts[e] += 1

        return render_template(
            "index.html",
            activities=activities,
            emotions=emotions,
            emotion_filter=emotion_filter,
            emotion_counts=emotion_counts,
        )
    
    @app.route("/practice")
    def practiceScreen():
        return render_template("practice.html")



    return app




app = create_app()

if __name__ == "__main__":

    flask_port = int(os.getenv("FLASK_PORT", "5001"))
    app.run(host="0.0.0.0", port=flask_port)
