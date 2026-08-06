#!/bin/sh
set -e

# Ensure backend data file exists
mkdir -p /app/backend
touch /app/backend/data.json

# Start Gunicorn to serve the Flask backend on localhost:5000
cd /app
# Run gunicorn in background
gunicorn --workers 2 --bind 127.0.0.1:5000 backend.app:app &

# Start nginx in the foreground (will serve frontend and proxy /api)
nginx -g 'daemon off;'
