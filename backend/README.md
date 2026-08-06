# Backend (Flask)

Flask API for the BMO agent simulator. It powers the tool selection, multi-step
reasoning, streaming step events, and persisted history.

---

## Requirements

- Python 3.10+ (tested on Python 3.12)
- pip
- Docker (optional, for containerized run)

---

## Setup

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate it

**PowerShell (Windows)**
```powershell
. .\.venv\Scripts\Activate.ps1
```

**Command Prompt (Windows)**
```bat
.venv\Scripts\activate.bat
```

**Git Bash / MSYS / WSL**
```bash
source .venv/Scripts/activate
```

If the venv does not exist yet, create it with:
```bash
python -m venv .venv
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## How to run

### Local

Recommended:
```bash
python -m backend
```

Alternative WSGI run (same entrypoint used in Docker):
```bash
gunicorn -w 2 -b 127.0.0.1:5000 backend.app:app
```

> Note: `python app.py` is not recommended because it bypasses package context.

### Docker

From the repository root:
```bash
docker build -t bmo-coding-challenge:latest .
docker run -d --name bmo-coding-challenge -p 80:80 bmo-coding-challenge:latest
```

Open:
```text
http://localhost
```

Stop:
```bash
docker rm -f bmo-coding-challenge
```

---

## API Endpoints

### `POST /api/tasks`
Submits a task and returns the full agent response.

**Request body**
```json
{ "task": "What is the weather in Toronto?" }
```

**Response**
```json
{
  "id": "uuid",
  "task": "What is the weather in Toronto?",
  "output": "The weather in Toronto is Cloudy with a temperature of 27°C.",
  "steps": ["Step 1: ..."],
  "tools": ["WeatherMockTool"],
  "timestamp": "2026-08-06T00:00:00Z"
}
```

### `POST /api/tasks/stream`
Streams step-by-step agent progress using Server-Sent Events (SSE).

**Request body**
```json
{ "task": "What is the weather in Toronto? Also, calculate 2+2" }
```

**Response**
- `Content-Type: text/event-stream`
- Emits `step` events as the agent reasons
- Emits a final `result` event with the completed output

### `GET /api/tasks`
Returns persisted task history from `data.json`.

---

## Implementation Overview

### `agent.py`

Contains the `AgentController`, which:
- chooses the right tool(s) for a user request
- splits multi-part requests into subtasks
- executes tools with retry handling
- composes the final human-readable response
- streams step-by-step reasoning events through `handle_stream()`

### `tools.py`

Contains the individual tools used by the agent:
- `TextProcessorTool` — uppercase, lowercase, reverse, title case, and word count
- `CalculatorTool` — safe arithmetic evaluation using a restricted AST
- `WeatherMockTool` — deterministic mock weather responses by city name

Each tool returns a readable result plus step details that are used in the
chat trace and the test results module.

---

## Tests

Run the backend unit tests from the `backend/` folder:

```bash
pytest -q
```

The test suite covers:
- tool selection
- tool execution
- multi-tool reasoning
- streaming events

---

## Notes

- History is persisted in `backend/data.json`.
- The frontend dev server proxies `/api` to `http://localhost:5000`.
- In Docker, nginx serves the frontend and proxies `/api/*` to the backend.
