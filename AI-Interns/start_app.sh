#!/bin/bash
# Startup script for AI-Interns Flask app with venv

# Activate the virtual environment
source /Users/pranoy/Desktop/AI-Practice/venv/bin/activate

echo "✓ Virtual environment activated"
echo "Python: $(which python)"
echo ""

# Start the Flask app
cd "$(dirname "$0")"
python app.py
