"""Main Flask application for Bird Detection Dashboard."""

import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from pymongo import MongoClient, errors as mongo_errors
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://admin:admin123@mongodb:27017/?authSource=admin",
)
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "birdnet_db")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
detections_collection = db["detections"]
users_collection = db["users"]

# Ensure username is unique in the users collection.
# create_index is idempotent — safe to call on every startup.
users_collection.create_index("username", unique=True)

# ---------------------------------------------------------------------------
# Flask-Login setup
# ---------------------------------------------------------------------------

login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    """Minimal user model backed by MongoDB."""

    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(user_id):
    """Return User if the username exists in MongoDB, else None."""
    doc = users_collection.find_one({"username": user_id})
    if doc:
        return User(user_id)
    return None


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------


@app.route("/login", methods=["GET", "POST"])
def login():
    """Show login form and handle submission."""
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        doc = users_collection.find_one({"username": username})
        if doc and check_password_hash(doc["password_hash"], password):
            login_user(User(username))
            return redirect(url_for("home"))
        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Show registration form and create a new user in MongoDB."""
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not password:
            error = "Username and password are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords do not match."
        else:
            try:
                users_collection.insert_one(
                    {
                        "username": username,
                        "password_hash": generate_password_hash(password),
                    }
                )
                login_user(User(username))
                return redirect(url_for("home"))
            except mongo_errors.DuplicateKeyError:
                error = "Username already taken."

    return render_template("register.html", error=error)


@app.route("/logout")
@login_required
def logout():
    """Log the current user out and redirect to login."""
    logout_user()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


@app.route("/")
@login_required
def home():
    """Render the main dashboard."""
    return render_template("index.html", username=current_user.id)


# ---------------------------------------------------------------------------
# API routes (all require login)
# ---------------------------------------------------------------------------


@app.route("/start")
@login_required
def start():
    """Start listening"""
    print("listening started")
    return {"status": "listening started"}


@app.route("/stop")
@login_required
def stop():
    """End listening"""
    print("listening stopped")
    return {"status": "listening stopped"}


@app.route("/detections")
@login_required
def detections():
    """Return recent detections from MongoDB."""
    docs = list(
        detections_collection.find({}, {"_id": 0}).sort("created_at", -1).limit(20)
    )

    response_docs = [
        {
            "recording_id": str(doc["recording_id"]) if "recording_id" in doc else None,
            "species_name": doc.get("species_name"),
            "confidence": doc.get("confidence"),
            "created_at": (
                doc["created_at"].isoformat() if "created_at" in doc else None
            ),
        }
        for doc in docs
    ]

    return jsonify(response_docs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
