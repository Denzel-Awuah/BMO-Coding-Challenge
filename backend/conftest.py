import sys
import os

# Ensure the backend package root is on sys.path so that test files can
# import modules using absolute names (e.g. `from agent import AgentController`)
# regardless of the working directory pytest is invoked from.
sys.path.insert(0, os.path.dirname(__file__))
