#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🔧 Creating virtual environment..."
python3 -m venv venv

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing required packages..."
pip install --upgrade pip
pip install python-dotenv langchain_openai langchain_community chromadb youtube-transcript-api streamlit
pip install pytube pypdf web3 SpeechRecognition opencv-python beautifulsoup4 arxiv wikipedia

echo "🚀 Running embedding script..."
python3 embedding.py

echo "🎛️ Launching Streamlit app..."
streamlit run inference.py