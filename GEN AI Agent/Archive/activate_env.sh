#!/bin/bash
# Convenience script to activate AI-Practice venv for Archive project

# Activate the venv from AI-Practice
source /Users/pranoy/Desktop/AI-Practice/venv/bin/activate

echo "✓ Activated AI-Practice venv"
echo "Python: $(which python)"
echo "Current directory: $(pwd)"
echo ""
echo "You can now run:"
echo "  python main.py build --excel your_file.xlsx"
echo "  python main.py generate --excel your_file.xlsx"
echo "  python main.py query 'your question'"
