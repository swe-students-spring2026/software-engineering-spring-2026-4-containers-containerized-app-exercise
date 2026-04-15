from io import BytesIO
from flask import Flask, flash, redirect, render_template, request, url_for, session
import asyncio, os

app = Flask(__name__)

#get the secret key from env
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

@app.route("/", methods=["GET", "POST"])
def new_run():
    if request.method == "GET":
        return render_template("index.html")
    # if request.method == "POST":
        # path 1: getting ai image recognition

if __name__ == "__main__":
    app.run(debug=True)
