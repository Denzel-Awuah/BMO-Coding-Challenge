# BMO Coding Challenge — Tech Lead, AI Engineering

A full-stack AI agent simulator built with React (frontend) and Python/Flask (backend).
The agent accepts natural-language tasks, selects one or more tools to fulfil them,
streams its reasoning steps in real time, and returns a composed, human-readable response.

---

## Project Structure

```
.
├── backend/          # Flask API — AgentController + Tools
├── frontend/         # React + Vite SPA
├── docker/           # nginx config and container start script
├── Dockerfile        # Multi-stage build (Node → Python + nginx)
└── README.md
```

---

## Environment Requirements

| Tool | Minimum version | Notes |
|------|----------------|-------|
| Python | 3.10 | Developed and tested on 3.12 |
| Node.js | 18 | npm 9+ included |
| Docker | 20 | Only required for container option |
| npm | 9 | Comes bundled with Node 18 |

---

## Dependencies

### Backend (`backend/requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 2.2.5 | HTTP API framework |
| flask-cors | 3.0.10 | Cross-origin requests from the frontend dev server |
| gunicorn | 21.2.0 | Production WSGI server (used inside Docker) |
| pytest | 7.4.2 | Unit test runner |

### Frontend (`frontend/package.json`)

| Package | Version | Purpose |
|---------|---------|---------|
| react / react-dom | 18.x | UI framework |
| vite | 5.x | Dev server and production bundler |
| @vitejs/plugin-react | 4.x | JSX transform for Vite |
| vitest | 0.34.x | Unit test runner (Vite-native) |
| @testing-library/react | 14.x | Component rendering in tests |
| @testing-library/jest-dom | 6.x | DOM assertion matchers |
| jsdom | 22.x | Headless browser environment for tests |

---

## How to Run

### Option 1 — Local (recommended for development)

**Backend**
```bash
# From the repository root
python -m venv .venv
# Windows PowerShell
. .\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r backend/requirements.txt
python -m backend          # runs on http://localhost:5000
```

**Frontend** (separate terminal)
```bash
cd frontend
npm install
npm start                  # runs on http://localhost:5173
```

Vite automatically proxies `/api` requests to `http://localhost:5000`, so no extra configuration is needed.

### Option 2 — Docker (single full-stack container)

```bash
# Build
docker build -t bmo-agentcoding-challenge:latest .

# Run
docker run -d --name bmo-agentcoding-challenge -p 80:80 bmo-agentcoding-challenge:latest

# Open in browser
http://localhost

# Stop
docker rm -f bmo-agentcoding-challenge

# View logs
docker logs -f bmo-agentcoding-challenge
```

Inside the container nginx serves the static frontend and proxies `/api/*` to the Gunicorn-managed Flask backend on port 5000.

---

## Running Tests

### Backend
```bash
# Activate the virtual environment first (see above), then:
cd backend
pytest -q
```

### Frontend
```bash
cd frontend
npm test
```

---

## Features

- **Agent with multi-step reasoning** — the planner splits chained user requests
  (separated by `.`, `?`, `Also,`, `Additionally,` etc.) into independent subtasks,
  selects the right tool for each, and composes the outputs into a single answer.
- **Real-time streaming** — the backend exposes `POST /api/tasks/stream` (Server-Sent
  Events). The frontend reads the stream and renders each reasoning step as it arrives,
  with a 0.5 s delay per step so the trace is clearly visible.
- **Retry / error handling** — every tool execution is retried up to 2 times on
  failure; errors are recorded in the step trace and the agent continues best-effort
  with remaining subtasks.
- **Three tools**
  - `TextProcessorTool` — uppercase, lowercase, reverse, title case, word count
  - `CalculatorTool` — safe AST-based arithmetic evaluation (no `eval` on arbitrary code)
  - `WeatherMockTool` — deterministic mock weather by city name
- **Persistent history** — results are stored in `backend/data.json` and loaded into
  the sidebar on page load.
- **View Test Results** — a modal with 26 pre-computed example queries (single-tool and
  multi-tool) to demonstrate the agent's capabilities without having to type them.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tasks` | Submit a task; returns full JSON result |
| `GET` | `/api/tasks` | Retrieve persisted history |
| `POST` | `/api/tasks/stream` | Submit a task; streams SSE step events then a final result |

### POST /api/tasks — request body
```json
{ "task": "What is the weather in Toronto?" }
```

### POST /api/tasks — response
```json
{
  "id": "uuid",
  "task": "What is the weather in Toronto?",
  "output": "The weather in Toronto is Cloudy with a temperature of 27°C.",
  "steps": ["Step 1: ...", "Step 2: ..."],
  "tools": ["WeatherMockTool"],
  "timestamp": "2026-08-06T00:00:00Z"
}
```

---

## Assumptions and Tradeoffs

| Decision | Rationale |
|----------|-----------|
| JSON file for persistence | Keeps the stack dependency-free and self-contained; a relational or document database would be the next step for a production deployment. |
| Deterministic weather mock | The challenge does not require a live API; the mock is reproducible and testable without network access or API keys. |
| AST-based calculator | Avoids executing arbitrary Python via `eval`; only a safe subset of numeric expression nodes is allowed. |
| Single-container Docker image | Simplifies the run-it-locally experience for evaluators; a `docker-compose` split (frontend + backend) would be preferred for production for independent scaling and tighter security. |
| `text/event-stream` over WebSockets | SSE is simpler to implement over standard HTTP and works well for one-way server→client push without an additional library. |
| Simple sentence-boundary planner | Regex-based splitting is transparent, testable, and fast. A production agent would use an LLM or a proper NLP pipeline for intent decomposition. |
| `time.sleep` step delay | Makes the streaming visually clear in the UI; in production this would be removed and real asynchronous tool latency would provide natural pacing. |

---

## Time Spent

| Phase | Approximate time |
|-------|-----------------|
| Initial architecture and scaffolding | 1 h |
| Backend agent, tools, and API | 2 h |
| Frontend React app and styling | 2 h |
| Docker containerisation | 1 h |
| Unit tests (backend + frontend) | 1 h |
| Bonus features (streaming, multi-step, retry) | 2 h |
| UI polish, bug fixes, and documentation | 1 h |
| **Total** | **~10 h** |

---

## What I Would Improve With More Time

- **LLM-powered intent router** — replace the regex planner with a lightweight model
  (e.g. a fine-tuned classifier or a prompt to a small open-weights LLM) so the agent
  can handle ambiguous, complex, or entirely novel task phrasings.
- **Persistent storage** — swap `data.json` for SQLite (via SQLAlchemy) or PostgreSQL
  to support concurrent writes, pagination, and search.
- **Streaming with async Flask** — migrate to `asyncio`-based Flask (or FastAPI) to
  support many concurrent SSE connections without blocking worker threads.
- **More tools** — currency conversion, unit conversion, date arithmetic, and a
  web-search stub would significantly broaden the agent's usefulness.
- **Authentication** — add a simple token or session layer so history is per-user.
- **End-to-end tests** — add Playwright or Cypress tests that boot the stack and verify
  the full user journey (type a query → see steps stream → see final answer in history).
- **CI/CD pipeline** — GitHub Actions workflow to run backend and frontend tests on
  every push and build + push the Docker image to a registry on merge to main.
- **docker-compose** — split the single container into separate frontend (nginx) and
  backend (gunicorn) services for independent scaling and cleaner separation.