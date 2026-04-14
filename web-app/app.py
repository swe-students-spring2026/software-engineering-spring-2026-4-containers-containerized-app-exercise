import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
    UserMixin,
)
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from bson.objectid import ObjectId
from database import get_users_collection, get_speeches_collection

users_coll = get_users_collection()
speeches_coll = get_speeches_collection()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = None

class User(UserMixin):

    def __init__(self, doc):
        self.id = str(doc["_id"])
        self.username = doc.get("username", "")

    @staticmethod
    def get_by_username(username):
        doc = users_coll.find_one({"username": username.lower().strip()})
        return User(doc) if doc else None

    @staticmethod
    def create(username, password):
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
    try:
        doc = users_coll.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    return User(doc) if doc else None

@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
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
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        password_check = request.form.get("password2") or ""

        if not username:
            flash("Please enter a username.")
            return render_template("signup.html")
        if not password:
            flash("Please enter a password.")
            return render_template("signup.html")
        if password != password_check:
            flash("Passwords do not match")
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
    logout_user()
    session.pop("_flashes", None)
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Shows all the speeches the user has recorded."""
    # TODO
    speeches = []
    return render_template("dashboard.html", speeches=speeches)

@app.route("/record")
@login_required
def record():
    """This will be the page that users record and name their speech."""
    return render_template("record.html")

@app.route("/delete/<speech_id>", methods=["POST"])
@login_required
def delete(speech_id):
    """This will allow users to delete a speech they have made."""
    # TODO
    return redirect(url_for("dashboard"))

@app.route("/submit", methods=["POST"])
@login_required
def submit():
    """Send the audio file and the name of the speech to the ML client."""
    # TODO
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)






