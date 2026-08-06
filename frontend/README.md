Frontend (React + Vite)

How to run:

1. Ensure Node.js is installed (Node 18+ recommended)
2. From the frontend folder:
   npm install
   npm start

This starts a development server (Vite) at http://localhost:5173 by default.
By default the frontend uses a relative API path (/api) so it works when the frontend is served by the same host (for example when built into the Docker image and served by nginx). When developing locally with Vite, the dev server has a proxy configured so requests to /api are forwarded to http://localhost:5000. If you prefer to override the API base explicitly, set the VITE_API_BASE environment variable (e.g. VITE_API_BASE=http://localhost:5000) before starting the dev server.

Notes:
- Enter tasks in the input box and submit. The UI shows the last result and the persisted history.

Running unit tests
-------------------

1. Install dependencies if not already installed:
   npm install

2. Run the unit tests (uses Vitest + React Testing Library):
   npm test

3. For an interactive watch mode during development:
   npm run test:watch

Test files are located under frontend/src/components/__tests__ and cover the ChatWindow and Sidebar components.
