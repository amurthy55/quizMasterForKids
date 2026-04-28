#!/bin/bash

# Voice Quiz Master Setup Script
echo "Setting up Voice Quiz Master..."

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Install system dependencies for TTS
echo "Installing system TTS packages..."
sudo apt update
sudo apt install -y espeak portaudio19-dev python3-pyaudio

# Install optional TTS engine (better quality)
echo "Installing festival TTS (optional, better quality)..."
sudo apt install -y festival

echo "Setup complete!"
echo ""
echo "Before running, set your OpenAI API key:"
echo "export OPENAI_API_KEY='your-openai-api-key-here'"
echo ""
echo "Then run:"
echo "python3 voice_quiz_master.py"
