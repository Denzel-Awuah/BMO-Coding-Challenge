# Frontend (React + Vite)

React SPA for the BMO agent simulator. It streams agent reasoning steps in real
time, displays the execution trace, and persists chat history in the sidebar.

---

## Requirements

- Node.js 18+
- npm 9+

---

## How to Run

### Local

```bash
cd frontend
npm install
npm start
```

Opens the Vite dev server at **http://localhost:5173**.

Vite automatically proxies `/api` requests to `http://localhost:5000`, so the
backend must also be running locally. See `backend/README.md` for setup instructions.

To override the API base URL explicitly:
```bash
VITE_API_BASE=http://localhost:5000 npm start
```

### Docker

Run the full stack from the repository root:
```bash
docker build -t bmo-agentcoding-challenge:latest .
docker run -d --name bmo-agentcoding-challenge -p 80:80 bmo-agentcoding-challenge:latest
```

Open **http://localhost** in your browser. The frontend is served by nginx inside
the container, which also proxies `/api/*` to the Flask backend.

Stop the container:
```bash
docker rm -f bmo-agentcoding-challenge
```

---

## Tests

```bash
cd frontend
npm install       # if not already done
npm test          # single run
```

For interactive watch mode during development:
```bash
npm run test:watch
```

Test files are located in `frontend/src/components/__tests__/` and cover:
- `ChatWindow` — message rendering and composer
- `Sidebar` — history items, section headings, and tool tag visibility
- `Composer` — input, submit, and clear behaviour
- `Message` — user and assistant bubble rendering
- `TestResultsModal` — modal open/close and data loading

---

## Notes

- API base defaults to relative `/api` so it works in both local dev and Docker.
- History is loaded from `GET /api/tasks` on page load and updated after each task.
- The agent streams execution steps via SSE; each step appears in the chat bubble
  in real time before the final answer is shown.
