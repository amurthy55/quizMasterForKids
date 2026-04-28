import os
from datetime import datetime

class QuizConfig:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    
    # Voice Settings
    SAMPLE_RATE = 16000
    MODEL_PATH = "vosk-model-small-en-us-0.15"
    
    # Audio sensitivity settings
    MIN_WORDS_FOR_PROCESSING = 1  # Allow single word answers for math
    MIN_CHAR_LENGTH = 1  # Allow single character answers
    SILENCE_BLOCKS = 30  # Wait longer for clearer speech (better accuracy)
    
    # Kid-friendly timing settings
    RESPONSE_PAUSE_TIME = 2.0  # Seconds to pause after response
    SENTENCE_PAUSE_TIME = 1.5  # Seconds to pause between sentences
    SPEECH_RATE_SLOWDOWN = 80  # How much to slow down speech rate
    
    # Context File
    CONTEXT_FILE = "quiz_context.json"
    
    # System Prompt for Kid-Friendly Quiz Master
    SYSTEM_PROMPT = """You are a friendly quiz master for children aged 6-10 years. Your role is to:

1. Ask age-appropriate science questions
2. Give encouraging feedback
3. Explain concepts simply
4. Keep answers brief and clear
5. Be patient and fun

IMPORTANT: You're receiving speech-to-text input that may have errors. 
If a word doesn't make sense, try to guess what the child meant based on context.

Examples:
- If child says "mortar" when talking about engines, they probably meant "motor"
- If something seems unclear, ask for clarification gently

Keep responses conversational and under 30 words when possible.
Use simple vocabulary that 6-10 year olds understand."""

    @staticmethod
    def get_context_file_path():
        return os.path.join(os.path.dirname(__file__), QuizConfig.CONTEXT_FILE)
