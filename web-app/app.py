import os
import pymongo
from flask import Flask, render_template
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
    connection = pymongo.MongoClient(mongo_uri)
    app.db = None
    ''''change to app.db = connection[actual name] '''

    @app.route("/")
    def home():
        """
        Main dashboard route.
        Returns dummy data if MongoDB is not connected.
        """
        if app.db is not None:

            activities = list(app.db.analysis.find().limit(10))
        else:
            activities = [
                {"name": "System", "message": "Running in offline mode (No DB)"},
                {"name": "ML Client", "message": "Waiting for connection..."},
            ]

        return render_template("index.html", activities=activities)

    return app


app = create_app()

if __name__ == "__main__":

    flask_port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host="0.0.0.0", port=flask_port)
