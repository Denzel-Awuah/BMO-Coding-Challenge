from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from .agent import AgentController

# Note: This module is intended to be imported as a package module (backend.app)
# For local development run using: python -m backend
# In production/docker we use a WSGI server such as gunicorn with the module path backend.app:app

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

app = Flask(__name__)
CORS(app)
agent = AgentController()


def load_history():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_entry(entry):
    history = load_history()
    history.insert(0, entry)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


@app.route("/api/tasks", methods=["POST"])
def submit_task():
    payload = request.get_json() or {}
    task_text = payload.get("task")
    if not task_text:
        return jsonify({"error": "task field is required"}), 400

    result = agent.handle(task_text)
    # Persist
    entry = {
        "id": result.get("id"),
        "task": task_text,
        "output": result.get("output"),
        "steps": result.get("steps"),
        "tools": result.get("tools"),
        "timestamp": result.get("timestamp"),
    }
    save_entry(entry)
    return jsonify(result)


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    history = load_history()
    return jsonify(history)


if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
