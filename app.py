import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "measles-sentinel-secret-2024")
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/symptoms")
def symptoms():
    return render_template("symptoms.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/scanning")
def scanning():
    return render_template("scanning.html")


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "app": "Measles Sentinel"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
