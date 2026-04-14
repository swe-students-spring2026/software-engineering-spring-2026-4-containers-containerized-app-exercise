import os
import pymongo
from flask import Flask, render_template, jsonify
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
        connection = pymongo.MongoClient(mongo_uri)
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
        if app.db is not None:

            activities = list(app.db.scans.find().limit(10))
        else:
            activities = [
                {"name": "System", "message": "Running in offline mode (No DB)"},
                {"name": "ML Client", "message": "Waiting for connection..."},
            ]

        return render_template("index.html", activities=activities)

    return app


app = create_app()

if __name__ == "__main__":

    flask_port = int(os.getenv("FLASK_PORT", "5001"))
    app.run(host="0.0.0.0", port=flask_port)
