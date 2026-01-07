#!/bin/bash
# Dashboard Bot Execution Script for Linux/WSL

# Navigate to script directory
cd "$(dirname "$0")"

# Check for virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
     echo "Activating virtual environment (fallback name)..."
     source venv/bin/activate
else
    echo "[ERROR] Virtual environment not found!"
    echo "Please set up the environment first (e.g., ./install.sh)"
    exit 1
fi

echo "Starting Dashboard Bot..."
python3 agent.py "$@"
