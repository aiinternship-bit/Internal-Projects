#!/bin/bash
# Startup script for AI-Interns Flask app with venv

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Navigate to the parent directory (Internal-Projects) to find venv
INTERNAL_PROJECTS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate the virtual environment in Internal-Projects directory
if [ -f "$INTERNAL_PROJECTS_DIR/venv/bin/activate" ]; then
    source "$INTERNAL_PROJECTS_DIR/venv/bin/activate"
else
    echo "Error: Virtual environment not found!"
    echo "Expected location: $INTERNAL_PROJECTS_DIR/venv/bin/activate"
    echo ""
    echo "Please create a virtual environment first:"
    echo "  cd $INTERNAL_PROJECTS_DIR"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo "✓ Virtual environment activated"
echo "Python: $(which python)"
echo ""

# Start the Flask app
cd "$(dirname "$0")"
python app.py
