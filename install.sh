#!/bin/bash

# Bug Fix Evaluator Installation Script
echo "Installing Bug Fix Evaluator..."

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating a virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install the package in development mode
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing Bug Fix Evaluator in development mode..."
pip install -e .

echo "Installation complete!"
echo "To use Bug Fix Evaluator, activate the virtual environment with:"
echo "  source venv/bin/activate"
echo "Then run the command:"
echo "  bug-fix-eval --help" 