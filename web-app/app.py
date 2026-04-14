from flask import Flask, request, jsonify, render_template
from machine_learning_client.joke_ranking import analyze_text
from datetime import datetime

app = Flask(__name__)

# initialize db


@app.route("/")
def dashboard():
    return render_template("dashboard.html") # @TODO replace dashboard.html when we get frontend


@app.route("/api/analysis", methods=["POST"])
def add_analysis():
    data = request.get_json(force=True)
    text = data.get("text")

    if not text:
        return jsonify({"error": "missing text"}), 400

    classification, score = analyze_text(text)

    record = {
        "timestamp": datetime.now().isoformat(),
        "input": text,
        "classification": classification,
        "score": score,
    }

    # @TODO save to db 

    return jsonify({"status": "success"}), 201


@app.route("/api/analysis", methods=["GET"])
def get_analysis():
    # @TODO get list of all analysis from db 
    return #return json version of fetch from db


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)