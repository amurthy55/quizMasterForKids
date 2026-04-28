#!/usr/bin/env python3
import os
import json
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

class SpeechToText:
    def __init__(self, model_path=None):
        """Initialize speech recognition with Vosk model"""
        if model_path is None:
            model_path = "vosk-model-small-en-us-0.15"
        
        if not os.path.exists(model_path):
            print(f"Error: Model not found at {model_path}")
            print("Please download a Vosk model first:")
            print("wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
            print("unzip vosk-model-small-en-us-0.15.zip")
            return
        
        print("Loading Vosk model...")
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.audio_queue = queue.Queue()
        
    def audio_callback(self, indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio callback status: {status}")
        self.audio_queue.put(bytes(indata))
    
    def start_listening(self):
        """Start real-time speech recognition"""
        print("Starting speech recognition...")
        print("Speak into your microphone. Press Ctrl+C to stop.")
        print("-" * 50)
        
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, 
                                 dtype='int16', channels=1, 
                                 callback=self.audio_callback):
                print("Listening...")
                
                while True:
                    data = self.audio_queue.get()
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        if result['text']:
                            print(f"You said: {result['text']}")
                    else:
                        # Partial result (optional - can be noisy)
                        partial = json.loads(self.recognizer.PartialResult())
                        # Uncomment below to see partial results
                        # if partial['partial']:
                        #     print(f"Partial: {partial['partial']}", end='\r')
                        
        except KeyboardInterrupt:
            print("\nStopping speech recognition...")
        except Exception as e:
            print(f"Error: {e}")

def main():
    # Check if model exists, if not provide download instructions
    model_path = "vosk-model-small-en-us-0.15"
    
    if not os.path.exists(model_path):
        print("Vosk model not found. Please download it first:")
        print("1. wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        print("2. unzip vosk-model-small-en-us-0.15.zip")
        print("3. Run this script again")
        return
    
    # Initialize and start speech recognition
    stt = SpeechToText(model_path)
    if stt.model:  # Only start if model loaded successfully
        stt.start_listening()

if __name__ == "__main__":
    main()
