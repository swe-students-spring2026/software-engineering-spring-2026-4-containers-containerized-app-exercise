"""Flask web application for SpeechCoach."""
import datetime
import os

import ffmpeg
import requests
from bson.objectid import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db import users_collection, speeches_collection

load_dotenv()

users_coll = users_collection
speeches_coll = speeches_collection

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = None

class User(UserMixin):
    """User functions to create and search for users"""

    def __init__(self, doc):
        """Initialize user from MongDB"""
        self.id = str(doc["_id"])
        self.username = doc.get("username", "")

    @staticmethod
    def get_by_username(username):
        """Finds the user by their username"""
        doc = users_coll.find_one({"username": username.lower().strip()})
        return User(doc) if doc else None

    @staticmethod
    def create(username, password):
        """Creates a new user"""
        username = username.lower().strip()
        if users_coll.find_one({"username": username}):
            return None
        doc = {
            "username": username,
            "password_hash": generate_password_hash(
                password, method="pbkdf2:sha256"
            ),
            "created_at": datetime.datetime.utcnow(),
        }
        ins = users_coll.insert_one(doc)
        doc["_id"] = ins.inserted_id
        return User(doc)


@login_manager.user_loader
def load_user(user_id):
    """Load user by id for login"""
    try:
        doc = users_coll.find_one({"_id": ObjectId(user_id)})
    except InvalidId:
        return None
    return User(doc) if doc else None

@app.route("/")
@login_required
def index():
    """Redirects automatically to dashboard."""
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles users logging in"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if not username or not password:
            flash("Enter a username and password.")
            return render_template("login.html")
        user = User.get_by_username(username)
        if not user:
            flash("Invalid username or password.")
            return render_template("login.html")
        doc = users_coll.find_one({"username": username.lower()})
        if not doc or not check_password_hash(doc["password_hash"], password):
            flash("Invalid username or password")
            return render_template("login.html")
        login_user(user)
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handles new users signing up"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        password_check = request.form.get("password2") or ""

        if not username or not password:
            flash("Please enter a username and password.")
            return render_template("signup.html")
        if password != password_check:
            flash("Passwords do not match.")
            return render_template("signup.html")

        user = User.create(username, password)
        if not user:
            flash("Username already taken.")
            return render_template("signup.html")

        login_user(user)
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    """Log out of current user"""
    logout_user()
    session.pop("_flashes", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Shows all the speeches the user has recorded on the dashboard."""
    docs = list(speeches_coll.find({"user_id": current_user.id}).sort("timestamp", -1))
    for doc in docs:
        doc["id"] = str(doc["_id"])
    return render_template("dashboard.html", speeches=docs, user=current_user)

@app.route("/record")
@login_required
def record():
    """This will be the page that users record and name their speech."""
    return render_template("record.html")

@app.route("/delete/<speech_id>", methods=["POST"])
@login_required
def delete(speech_id):
    """This will allow users to delete a speech they have made."""
    try:
        oid = ObjectId(speech_id)
    except InvalidId:
        flash("Invalid speech id.")
        return redirect(url_for("dashboard"))
    speeches_coll.delete_one({
        "_id": oid,
        "user_id": current_user.id
    })
    flash("Speech deleted.")
    return redirect(url_for("dashboard"))

@app.route("/submit", methods=["POST"])
@login_required
def submit():
    """Sends a .wav audio file and the name of the speech to the ML client."""
    title = (request.form.get("title") or "").strip()
    audio_file = request.files.get("audio")

    if not title:
        flash("Please enter a title for your speech.")
        return redirect(url_for("record"))

    if not audio_file:
        flash("Please record your speech before submitting.")
        return redirect(url_for("record"))

    webm_path = f"temp_{current_user.id}.webm"
    wav_path = f"temp_{current_user.id}.wav"
    audio_file.save(webm_path)

    try:
        ffmpeg.input(webm_path).output(wav_path).run(overwrite_output=True)
    except ffmpeg.Error:
        flash("Could not process audio file. Please try again.")
        if os.path.exists(webm_path):
            os.remove(webm_path)
        return redirect(url_for("record"))

    try:
        with open(wav_path, "rb") as f:
            response = requests.post(
                os.environ.get("ML_CLIENT_URL", "http://localhost:5001/analyze"),
                files={"audio": f},
                data={
                    "title": title,
                    "user_id": current_user.id,},
                timeout=60,)
        if response.status_code != 200:
            flash("Something went wrong analyzing your speech. Please try again.")
            return redirect(url_for("record"))

    except requests.exceptions.RequestException:
        flash("Could not reach the analysis service. Please try again.")
        return redirect(url_for("record"))

    finally:
        if os.path.exists(webm_path):
            os.remove(webm_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

    flash("Speech analyzed successfully!")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
