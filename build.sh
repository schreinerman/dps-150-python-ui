#!/bin/bash
# Build script for macOS and Linux
# Automatically creates a venv and builds the app

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=== DPS-150 Native App Builder ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"
echo ""

# Create virtual environment if not present
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "[OK] Virtual environment created"
else
    echo "[OK] Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements-build.txt --quiet
echo "[OK] Dependencies installed"

echo ""
echo "Starting build process..."
echo ""

# Check if architecture argument is provided
if [ -n "$1" ]; then
    python build.py "$1"
else
    python build.py
fi

echo ""
echo "=== [SUCCESS] Build completed! ==="
echo "The application is in the 'dist' folder"
if [ "$(uname)" = "Darwin" ]; then
    echo "   -> dist/DPS150-Control.app"
elif [ "$(uname)" = "Linux" ]; then
    echo "   -> dist/DPS150-Control"
fi
echo ""

deactivate
