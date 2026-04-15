"""Main Flask application for Bird Detection Dashboard."""

from datetime import datetime
import random
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/start")
def start():
    """Start listening"""
    print("listening started")
    return {"status": "listening started"}


@app.route("/stop")
def stop():
    """End listening"""
    print("listening stopped")
    return {"status": "listening stopped"}


@app.route("/detections")
def detections():
    """Placeholder detection data (replace with DB later)"""
    birds = ["Sparrow", "Robin", "Blue Jay", "Cardinal"]
    fake_data = [
        {
            "name": random.choice(birds),
            "confidence": random.randint(70, 99),
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        for _ in range(5)
    ]
    return fake_data


if __name__ == "__main__":
    app.run(debug=True)
