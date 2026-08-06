from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Support both package execution (python -m backend / gunicorn backend.app:app)
# and direct script execution (python app.py from the backend directory).
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from backend.agent import AgentController
else:
    from .agent import AgentController

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


@app.route("/api/tasks/stream", methods=["POST"])
def stream_task():
    payload = request.get_json() or {}
    task_text = payload.get("task")
    if not task_text:
        return jsonify({"error": "task field is required"}), 400

    def event_stream():
        # accumulate step messages so final persisted entry contains the trace
        accumulated_steps = []
        for evt in agent.handle_stream(task_text):
            # if this is a step, collect for persistence
            if isinstance(evt, dict) and evt.get('type') == 'step':
                accumulated_steps.append(evt.get('data'))
                yield f"data: {json.dumps(evt)}\n\n"
            elif isinstance(evt, dict) and evt.get('type') == 'result':
                # persist final result with accumulated steps
                result_obj = evt.get('data')
                if isinstance(result_obj, dict):
                    entry = {
                        "id": result_obj.get("id"),
                        "task": result_obj.get("task"),
                        "output": result_obj.get("output"),
                        "steps": accumulated_steps,
                        "tools": result_obj.get("tools"),
                        "timestamp": result_obj.get("timestamp"),
                    }
                    try:
                        save_entry(entry)
                    except Exception as e:
                        # emit an event about persisting failure
                        err_evt = {"type": "step", "data": f"Failed to persist result: {str(e)}"}
                        yield f"data: {json.dumps(err_evt)}\n\n"
                # then yield the original result event
                yield f"data: {json.dumps(evt)}\n\n"
            else:
                # unknown event, just forward
                yield f"data: {json.dumps(evt)}\n\n"
        # final close
    return app.response_class(event_stream(), mimetype='text/event-stream')


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    history = load_history()
    return jsonify(history)


if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=5000, debug=True)
