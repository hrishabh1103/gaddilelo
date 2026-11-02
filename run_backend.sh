#!/usr/bin/env bash
# Script to run GaadiLelo FastAPI backend server
cd "$(dirname "$0")"

# Activate virtual environment if present
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
fi

export PYTHONPATH=.
echo "Starting GaadiLelo Backend API on http://localhost:8000..."
uvicorn backend.app.main:app --reload --port 8000

