"""Main Flask application for Bird Detection Dashboard."""

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
def end():
    """End listening"""
    print("listening stopped")
    return {"status": "listening stopped"}


if __name__ == "__main__":
    app.run(debug=True)
