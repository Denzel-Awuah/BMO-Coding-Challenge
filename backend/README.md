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
   python app.py

The backend serves two endpoints:
- POST /api/tasks  {"task": "<text>"}
  -> returns JSON with output, steps, tools, timestamp
- GET /api/tasks
  -> returns persisted history (data.json)

Data persistence uses data.json in the backend folder.
