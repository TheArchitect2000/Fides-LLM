#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set the virtual environment directory name
VENV_DIR="venv"

echo "🔍 Checking for virtual environment: $VENV_DIR"

# Step 1: Remove virtual environment folder
if [ -d "$VENV_DIR" ]; then
  sudo rm -rf "$VENV_DIR"
  echo "✅ Removed virtual environment folder: $VENV_DIR"
else
  echo "⚠️  No virtual environment folder named '$VENV_DIR' found."
fi

# Step 2: Remove all __pycache__ directories
echo "🧹 Removing all __pycache__ folders..."
find . -type d -name "__pycache__" -exec rm -r {} +
echo "✅ __pycache__ cleanup complete."

# Step 3: Remove all .pyc files
echo "🧹 Removing all .pyc files..."
find . -type f -name "*.pyc" -delete
echo "✅ .pyc cleanup complete."

# Step 4: Create virtual environment

echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Step 5: Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Step 6: Install required packages
echo "📦 Installing required packages..."
pip install --upgrade -r requirements.txt

# Step 7: Run embedding script
echo "🚀 Running embedding script..."
python3 embedding.py
