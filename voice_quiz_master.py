#!/usr/bin/env python3
import os
import json
import queue
import signal
import sys
import time
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

from quiz_config import QuizConfig
from context_manager import ContextManager
from openai_client import OpenAIClient
from tts_engine import TTSEngine

class VoiceQuizMaster:
    def __init__(self):
        self.setup_components()
        self.audio_queue = queue.Queue()
        self.running = False
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def setup_components(self):
        """Initialize all components"""
        print("Setting up Voice Quiz Master...")
        
        # Setup Vosk
        if not os.path.exists(QuizConfig.MODEL_PATH):
            print(f"Error: Vosk model not found at {QuizConfig.MODEL_PATH}")
            sys.exit(1)
        
        print("Loading Vosk model...")
        self.vosk_model = Model(QuizConfig.MODEL_PATH)
        self.vosk_recognizer = KaldiRecognizer(self.vosk_model, QuizConfig.SAMPLE_RATE)
        
        # Setup OpenAI client
        print("Setting up OpenAI client...")
        self.openai_client = OpenAIClient()
        
        # Setup TTS engine
        print("Setting up TTS engine...")
        self.tts_engine = TTSEngine()
        
        if not self.tts_engine.tts_method:
            print("Warning: No TTS available. Install espeak: sudo apt install espeak")
        
        print("Setup complete!")
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\nShutting down Voice Quiz Master...")
        self.running = False
    
    def audio_callback(self, indata, frames, time_info, status):
        """Audio callback for Vosk"""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def listen_for_speech(self):
        """Listen for speech and return recognized text"""
        print("\n🎤 Listening... (speak now)")
        
        try:
            with sd.RawInputStream(
                samplerate=QuizConfig.SAMPLE_RATE,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self.audio_callback
            ):
                silence_count = 0
                collected_text = ""
                
                while self.running:
                    data = self.audio_queue.get()
                    
                    if self.vosk_recognizer.AcceptWaveform(data):
                        result = json.loads(self.vosk_recognizer.Result())
                        text = result.get('text', '').strip()
                        
                        if text:
                            # Filter out very short or likely noise results
                            if len(text.split()) >= QuizConfig.MIN_WORDS_FOR_PROCESSING or len(text) >= QuizConfig.MIN_CHAR_LENGTH:
                                print(f"👦: {text}")
                                return text
                            else:
                                print(f"🔇 Ignored (too short): {text}")
                                continue
                    
                    # Check for silence to determine when user stops speaking
                    partial = json.loads(self.vosk_recognizer.PartialResult())
                    if not partial.get('partial'):
                        silence_count += 1
                        if silence_count > QuizConfig.SILENCE_BLOCKS and collected_text:
                            # Process what we have
                            if len(collected_text.split()) >= QuizConfig.MIN_WORDS_FOR_PROCESSING:
                                print(f"👦: {collected_text}")
                                return collected_text
                    else:
                        silence_count = 0
                        collected_text = partial.get('partial', '')
        
        except Exception as e:
            print(f"Audio error: {e}")
            return None
    
    def process_conversation(self):
        """Main conversation loop"""
        print("\n" + "="*50)
        print("🎓 VOICE QUIZ MASTER FOR KIDS 🎓")
        print("="*50)
        
        # Welcome message
        welcome_text = "Hello Avira! I'm your science quiz master. I'll ask fun questions about science. Are you ready to start?"
        print(f"🤖: {welcome_text}")
        self.tts_engine.speak(welcome_text)
        
        session_info = self.openai_client.get_session_info()
        print(f"Session ID: {session_info['session_id']}")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        
        while self.running:
            # Listen for user input
            user_text = self.listen_for_speech()
            
            if not user_text:
                continue
            
            # Check for exit commands
            if any(word in user_text.lower() for word in ['stop', 'quit', 'bye', 'goodbye']):
                goodbye_text = "Great job today! Thanks for playing with me. Bye bye!"
                print(f"🤖: {goodbye_text}")
                self.tts_engine.speak(goodbye_text)
                break
            
            # Check for clear context command
            if any(word in user_text.lower() for word in ['start over', 'new game', 'restart']):
                response = self.openai_client.clear_session()
                print(f"🤖: {response}")
                self.tts_engine.speak(response)
                continue
            
            # Get AI response
            print("🤔 Thinking...")
            ai_response = self.openai_client.chat_with_context(user_text)
            
            print(f"🤖: {ai_response}")
            
            # Speak the response
            self.tts_engine.speak(ai_response)
            
            # Longer pause for kids to think before next turn
            print("⏳ Take your time...")
            time.sleep(QuizConfig.RESPONSE_PAUSE_TIME)  # Pause after response
    
    def run(self):
        """Start the voice quiz master"""
        try:
            self.process_conversation()
        except KeyboardInterrupt:
            pass
        finally:
            print("\nQuiz session ended. Goodbye!")
            # Show session summary
            session_info = self.openai_client.get_session_info()
            print(f"Session completed: {session_info['message_count']} messages exchanged")

def main():
    """Main entry point"""
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found!")
        print("Please set it with: export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)
    
    # Create and run quiz master
    quiz_master = VoiceQuizMaster()
    quiz_master.run()

if __name__ == "__main__":
    main()
