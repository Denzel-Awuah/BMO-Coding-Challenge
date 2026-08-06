BMO Coding Challenge - Tech Lead, AI Engineering

This repository contains a small full-stack implementation for the BMO coding challenge.

Structure
- frontend/: React + Vite frontend
- backend/: Flask backend implementing an Agent Controller and three Tools

How to run

Option 1: Run locally (frontend + backend)
1) Backend
- Recommended: create and activate a Python virtual environment
  python -m venv .venv
  .\.venv\Scripts\activate
- Install dependencies:
  pip install -r backend\requirements.txt
- Run backend:
  python -m backend

2) Frontend
- From frontend folder:
  npm install
  npm start
- Open the dev server (Vite) URL printed (default http://localhost:5173)

Option 2: Run with Docker (single full-stack container)
1) Build the image from the repository root:
   docker build -t bmo-agentcoding-challenge:latest .
2) Run the container:
   docker run -d --name bmo-coding-challenge -p 80:80 bmo-coding-challenge:latest
3) Open the app in your browser:
   http://localhost
4) The frontend and backend communicate through nginx in the container. API requests are served via /api/* and forwarded to the Flask backend.

Useful commands
- Stop the container:
  docker rm -f bmo-agentcoding-challenge
- View logs:
  docker logs -f bmo-agentcoding-challenge

Notes
- The frontend posts tasks to /api/tasks and reads history from GET /api/tasks.
- When running locally with Vite, requests are proxied to http://localhost:5000 automatically.
- When running inside Docker, the frontend uses the same host path /api and nginx proxies the request to the backend service.
- Persistence: backend/data.json stores history as JSON

Assumptions and tradeoffs
- No external APIs used; Weather is mocked deterministically
- Calculator uses a restricted AST-based evaluator to avoid executing arbitrary code
- Text tool uses simple heuristics for operations (uppercase/lowercase/wordcount/reverse/title)


What to improve with more time
- Improve natural-language parsing for tool selection
- Add more robust UI and validation
