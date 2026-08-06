Backend (Flask)

How to run:

1. Create a virtual environment (recommended)
   python -m venv .venv

   Activate the virtual environment (choose the command for your shell):
   - PowerShell (Windows):
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
     . .\.venv\Scripts\Activate.ps1

   - Command Prompt (cmd.exe) (Windows):
     .venv\Scripts\activate.bat

   - Git Bash / MSYS / WSL (bash):
     source .venv/Scripts/activate   # use .venv/bin/activate on Unix-style venvs

   If the .venv folder does not exist, run:
     python -m venv .venv


2. Install dependencies
   pip install -r requirements.txt

3. Run the app
   Recommended (clean package-aware run):
     python -m backend

   Alternatively, run with a WSGI server (used in Docker):
     gunicorn -w 2 -b 127.0.0.1:5000 backend.app:app

   Note: Running `python app.py` directly is not recommended because it doesn't execute with package context. Use `python -m backend` to ensure package-relative imports work correctly.

The backend serves two endpoints:
- POST /api/tasks  {"task": "<text>"}
  -> returns JSON with output, steps, tools, timestamp
- GET /api/tasks
  -> returns persisted history (data.json)

Data persistence uses data.json in the backend folder.

Running unit tests
------------------

1. Ensure the backend virtual environment is active (see steps above).
2. Install test dependencies (already included in requirements.txt):
   pip install -r requirements.txt
3. From the backend folder, run:
   pytest -q

The tests cover the core tools (TextProcessorTool, CalculatorTool, WeatherMockTool) and the AgentController selection and handling logic. They are located in backend/tests/.
