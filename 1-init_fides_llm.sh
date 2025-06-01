#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🔧 Creating virtual environment..."
python3 -m venv venv

echo "✅ Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing required packages..."
# pip install --upgrade pip
# pip install python-dotenv langchain_openai langchain_community chromadb youtube-transcript-api streamlit
# pip install pytube pypdf web3 SpeechRecognition opencv-python beautifulsoup4 arxiv wikipedia

pip install \
langchain==0.3.25 \
langchain_core==0.3.59 \
langchain_community==0.3.24 \
langchain_openai==0.3.16 \
langchain_text_splitters==0.3.8 \
openai==1.30.1 \
tiktoken==0.7.0 \
streamlit==1.45.0 \
chromadb==0.4.24 \
python-dotenv==1.0.1 \
requests==2.32.3 \
bs4==0.0.2 \
pytube==15.0.0 \
yt_dlp==2024.5.27 \
youtube-transcript-api==0.6.2 \
pypdf==4.2.0 \
gdown==5.1.0 \
GitPython==3.1.43

echo "🚀 Running embedding script..."
python3 embedding.py
