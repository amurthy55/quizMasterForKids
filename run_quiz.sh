#!/bin/bash

# Voice Quiz Master Runner Script
echo "Starting Voice Quiz Master..."

# Activate virtual environment
source quiz_master_env/bin/activate

# Run the JSON quiz master (no API costs)
python3 voice_quiz_master_json.py
