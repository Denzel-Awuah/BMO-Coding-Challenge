BMO Coding Challenge - Tech Lead, AI Engineering

This repository contains a small full-stack implementation for the BMO coding challenge.

Structure
- frontend/: React + Vite frontend
- backend/: Flask backend implementing an Agent Controller and three Tools

How to run

1) Backend
- Recommended: create and activate a Python virtual environment
  python -m venv .venv
  .\.venv\Scripts\activate
- Install dependencies:
  pip install -r backend\requirements.txt
- Run backend:
  python backend\app.py

2) Frontend
- From frontend folder:
  npm install
  npm start
- Open the dev server (Vite) URL printed (default http://localhost:5173)

Notes
- The frontend posts tasks to http://localhost:5000/api/tasks and reads history from GET /api/tasks
- Persistence: backend/data.json stores history as JSON

Assumptions and tradeoffs
- No external APIs used; Weather is mocked deterministically
- Calculator uses a restricted AST-based evaluator to avoid executing arbitrary code
- Text tool uses simple heuristics for operations (uppercase/lowercase/wordcount/reverse/title)

Time spent
- ~2 hours implementing a focused, minimal solution suitable for local run and extension

What to improve with more time
- Add unit tests for tools and agent
- Improve natural-language parsing for tool selection
- Add more robust UI and validation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
