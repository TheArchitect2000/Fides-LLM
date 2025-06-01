#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "🎛️ Launching Streamlit app..."
streamlit run inference.py