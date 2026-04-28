#!/bin/bash

# Voice Quiz Master Setup Script
echo "Setting up Voice Quiz Master..."

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv quiz_master_env

# Activate virtual environment
echo "Activating virtual environment..."
source quiz_master_env/bin/activate

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
echo "To run the quiz master:"
echo "source quiz_master_env/bin/activate"
echo "python3 voice_quiz_master_json.py"
echo ""
echo "For OpenAI version (optional):"
echo "export OPENAI_API_KEY='your-openai-api-key-here'"
echo "python3 voice_quiz_master.py"
