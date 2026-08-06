Frontend (React + Vite)

How to run:

1. Ensure Node.js is installed (Node 18+ recommended)
2. From the frontend folder:
   npm install
   npm start

This starts a development server (Vite) at http://localhost:5173 by default.
The frontend expects the backend to be running at http://localhost:5000 (default Flask port).

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
