# Voice Quiz Master for Kids

A complete voice-based interactive science quiz system for children aged 6-10, running on Raspberry Pi Zero 2W.

## Features

- 🎤 Real-time speech recognition with Vosk
- 🤖 OpenAI GPT integration for intelligent responses
- 🔊 Text-to-speech for voice feedback
- 💾 Local conversation context storage
- 👶 Kid-friendly interface and responses
- 🎓 Science-focused quiz content
- 🔄 Error correction for speech recognition mistakes

## Quick Setup

1. **Run setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

2. **Set OpenAI API key:**
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

3. Run the quiz master:

**OpenAI Version (requires API key):**
```bash
export OPENAI_API_KEY='your-openai-api-key-here'
python3 voice_quiz_master.py
```

**JSON Version (no API costs):**
```bash
python3 voice_quiz_master_json.py
```

## Manual Setup

### Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Install system dependencies:
```bash
sudo apt update
sudo apt install -y espeak portaudio19-dev python3-pyaudio festival
```

## Usage

1. Start the application with `python3 voice_quiz_master.py`
2. The system will welcome you and ask if you're ready to start
3. Speak naturally - it will recognize your speech and respond
4. Say "stop", "quit", or "bye" to end the session
5. Say "start over" or "new game" to reset the conversation

## Files Overview

### OpenAI Version
- `voice_quiz_master.py` - Main application with OpenAI integration
- `context_manager.py` - Conversation context handling
- `openai_client.py` - OpenAI API integration

### JSON Version (No API costs)
- `voice_quiz_master_json.py` - Main application using JSON questions
- `json_quiz_manager.py` - JSON quiz data manager
- `quiz_data/` - Directory containing quiz topic JSON files:
  - `planets.json` - Space and astronomy questions
  - `spelling_bee.json` - Spelling challenges
  - `parts_of_the_body.json` - Human body questions
  - `maths.json` - Basic math problems

### Shared Components
- `quiz_config.py` - Configuration settings
- `tts_engine.py` - Text-to-speech engine
- `speech_to_text.py` - Basic Vosk testing (original)
- `quiz_context.json` - Local conversation storage (auto-created)

## Raspberry Pi Zero 2W Optimization

- Uses Vosk small model (40MB) for low memory usage
- Offline speech recognition (~100MB RAM)
- Multiple TTS options (espeak, pyttsx3, gTTS)
- Efficient conversation context management

## Voice Commands

- **Start quiz**: "ready", "let's start", "yes"
- **Stop session**: "stop", "quit", "bye", "goodbye"  
- **Reset context**: "start over", "new game", "restart"

## Context & Memory

- Conversation history saved locally in `quiz_context.json`
- Context persists between sessions
- OpenAI receives conversation history for better responses
- Smart error correction for speech recognition mistakes

## Troubleshooting

**No audio input:**
- Check microphone permissions
- Ensure PortAudio is installed: `sudo apt install portaudio19-dev`

**TTS not working:**
- Install espeak: `sudo apt install espeak`
- Or install pyttsx3: `pip install pyttsx3`

**OpenAI API errors:**
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check internet connection for API calls

## Cost Management

- Uses GPT-3.5-turbo model (economical)
- Limits responses to 100 tokens
- Local context storage reduces API calls
- Optimized prompts for concise responses
