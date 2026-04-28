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
from json_quiz_manager import JsonQuizManager
from tts_engine import TTSEngine

class VoiceQuizMasterJson:
    def __init__(self):
        self.setup_components()
        self.audio_queue = queue.Queue()
        self.running = False
        self.current_state = "topic_selection"  # topic_selection, asking_question, verifying_answer
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def setup_components(self):
        """Initialize all components"""
        print("Setting up Voice Quiz Master (JSON Version)...")
        
        # Setup Vosk
        if not os.path.exists(QuizConfig.MODEL_PATH):
            print(f"Error: Vosk model not found at {QuizConfig.MODEL_PATH}")
            sys.exit(1)
        
        print("Loading Vosk model...")
        self.vosk_model = Model(QuizConfig.MODEL_PATH)
        self.vosk_recognizer = KaldiRecognizer(self.vosk_model, QuizConfig.SAMPLE_RATE)
        
        # Setup JSON Quiz Manager
        print("Setting up Quiz Manager...")
        self.quiz_manager = JsonQuizManager()
        
        # Setup TTS engine
        print("Setting up TTS engine...")
        self.tts_engine = TTSEngine()
        
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
    
    def process_topic_selection(self, user_input):
        """Process topic selection from user"""
        available_topics = self.quiz_manager.get_available_topic_names()
        
        # Check if user mentioned a specific topic
        if self.quiz_manager.select_topic(user_input):
            selected_topic = self.quiz_manager.current_topic
            # Convert topic name to user-friendly format
            friendly_name = selected_topic.replace('_', ' ')
            response = f"Great! I've selected the {friendly_name} topic. Let's start with a question!"
            self.current_state = "asking_question"
            return response
        
        # If no specific topic found, list available topics in friendly format
        friendly_topics = [topic.replace('_', ' ') for topic in available_topics]
        topics_list = ", ".join(friendly_topics)
        response = f"I didn't catch that. Available topics are: {topics_list}. Which topic would you like?"
        return response
    
    def process_question_answering(self, user_input):
        """Process answer to current question"""
        if not hasattr(self, 'current_question'):
            # Get a new question
            self.current_question = self.quiz_manager.get_random_question()
            if self.current_question:
                response = f"Here's your question: {self.current_question['question']}"
                return response
            else:
                return "Sorry, no questions available for this topic."
        
        # Check if user wants to switch topics
        if any(word in user_input.lower() for word in ['topic', 'category', 'change', 'different']):
            available_topics = self.quiz_manager.get_available_topic_names()
            friendly_topics = [topic.replace('_', ' ') for topic in available_topics]
            topics_list = ", ".join(friendly_topics)
            self.current_state = "topic_selection"
            return f"Sure! Available topics are: {topics_list}. Which topic would you like?"
        
        # Check if user is asking for a hint
        if any(word in user_input.lower() for word in ['hint', 'help', 'stuck']):
            hint = self.quiz_manager.get_hint(self.current_question)
            response = f"Here's a hint: {hint}. Now try again!"
            return response
        
        # Verify the answer
        is_correct, feedback = self.quiz_manager.verify_answer(self.current_question, user_input)
        
        if is_correct:
            explanation = self.quiz_manager.get_explanation(self.current_question)
            response = f"{feedback} {explanation} Let's move to the next question!"
            # Clear current question for next round
            delattr(self, 'current_question')
            # Get next question immediately
            self.current_question = self.quiz_manager.get_random_question()
            if self.current_question:
                response += f" Here's your next question: {self.current_question['question']}"
        else:
            explanation = self.quiz_manager.get_explanation(self.current_question)
            response = f"{feedback} {explanation} Let's try another question!"
            # Clear current question and get next one
            delattr(self, 'current_question')
            self.current_question = self.quiz_manager.get_random_question()
            if self.current_question:
                response += f" Here's your next question: {self.current_question['question']}"
        
        return response
    
    def process_conversation(self):
        """Main conversation loop"""
        print("\n" + "="*50)
        print("🎓 VOICE QUIZ MASTER FOR KIDS (JSON Version) 🎓")
        print("="*50)
        
        # Welcome message
        welcome_text = "Hello Avira! I'm your science quiz master. I can ask questions about planets, spelling bee, parts of the body, or maths. Which topic would you like?"
        print(f"🤖: {welcome_text}")
        self.tts_engine.speak(welcome_text)
        
        # Show available topics in friendly format
        available_topics = self.quiz_manager.get_available_topic_names()
        friendly_topics = [topic.replace('_', ' ') for topic in available_topics]
        print(f"Available topics: {', '.join(friendly_topics)}")
        
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
            
            # Check for restart command
            if any(word in user_text.lower() for word in ['start over', 'new game', 'restart']):
                self.quiz_manager.reset_topic()
                self.current_state = "topic_selection"
                response = "Great! Let's start over. Which topic would you like?"
                print(f"🤖: {response}")
                self.tts_engine.speak(response)
                continue
            
            # Process based on current state
            if self.current_state == "topic_selection":
                response = self.process_topic_selection(user_text)
            elif self.current_state == "asking_question":
                response = self.process_question_answering(user_text)
            else:
                response = "I'm not sure what to do. Let's start over. Which topic would you like?"
                self.current_state = "topic_selection"
            
            print(f"🤖: {response}")
            
            # Speak the response
            self.tts_engine.speak(response)
            
            # Longer pause for kids to think before next turn
            print("⏳ Take your time...")
            time.sleep(QuizConfig.RESPONSE_PAUSE_TIME)
    
    def run(self):
        """Start the voice quiz master"""
        try:
            self.process_conversation()
        except KeyboardInterrupt:
            pass
        finally:
            print("\nQuiz session ended. Goodbye!")
            # Show session summary
            stats = self.quiz_manager.get_stats()
            print(f"Session completed: {stats['history_count']} questions asked")

def main():
    """Main entry point"""
    # Create and run quiz master
    quiz_master = VoiceQuizMasterJson()
    quiz_master.run()

if __name__ == "__main__":
    main()
