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
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment if not present
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements-build.txt --quiet
echo "✓ Dependencies installed"

echo ""
echo "🔨 Starting build process..."
echo ""
python build.py

echo ""
echo "=== ✅ Build completed! ==="
echo "📂 The application is in the 'dist' folder"
if [ "$(uname)" = "Darwin" ]; then
    echo "   → dist/DPS150-Control.app"
elif [ "$(uname)" = "Linux" ]; then
    echo "   → dist/DPS150-Control"
fi
echo ""

deactivate
