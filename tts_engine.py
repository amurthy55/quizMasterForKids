import os
import subprocess
import tempfile
from quiz_config import QuizConfig

class TTSEngine:
    def __init__(self):
        self.tts_method = self.detect_tts_method()
    
    def detect_tts_method(self):
        """Detect available TTS method"""
        # Try to find available TTS options
        tts_methods = []
        
        # Check for espeak (most common on Linux)
        try:
            subprocess.run(['espeak', '--version'], capture_output=True, check=True)
            tts_methods.append('espeak')
        except:
            pass
        
        # Check for festival
        try:
            subprocess.run(['festival', '--version'], capture_output=True, check=True)
            tts_methods.append('festival')
        except:
            pass
        
        # Check for gtts (Google TTS - requires internet)
        try:
            import gtts
            tts_methods.append('gtts')
        except:
            pass
        
        # Check for pyttsx3 (offline TTS)
        try:
            import pyttsx3
            tts_methods.append('pyttsx3')
        except:
            pass
        
        if not tts_methods:
            print("Warning: No TTS engine found. Please install one:")
            print("  sudo apt install espeak  # Basic TTS")
            print("  pip install gtts pyttsx3  # Python TTS options")
            return None
        
        # Prefer offline options for Pi
        if 'pyttsx3' in tts_methods:
            return 'pyttsx3'
        elif 'espeak' in tts_methods:
            return 'espeak'
        elif 'gtts' in tts_methods:
            return 'gtts'
        else:
            return tts_methods[0]
    
    def speak(self, text):
        """Convert text to speech and play it"""
        if not text or not text.strip():
            return False
        
        text = text.strip()
        
        try:
            if self.tts_method == 'pyttsx3':
                return self.speak_pyttsx3(text)
            elif self.tts_method == 'espeak':
                return self.speak_espeak(text)
            elif self.tts_method == 'gtts':
                return self.speak_gtts(text)
            else:
                print(f"TTS method {self.tts_method} not implemented")
                return False
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
    
    def speak_pyttsx3(self, text):
        """Use pyttsx3 for offline TTS"""
        try:
            import pyttsx3
            import time
            
            print(f"🔊 Speaking: {text[:50]}...")  # Debug: show what's being spoken
            
            # Create fresh engine each time to avoid interruptions
            engine = pyttsx3.init()
            
            # Set kid-friendly voice properties - Much slower for kids
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 80)  # Much slower for kids to understand
            
            volume = engine.getProperty('volume')
            engine.setProperty('volume', 0.85)  # Clear volume
            
            # Add more natural speech parameters
            try:
                # Try to set voice pitch for more natural sound
                engine.setProperty('pitch', 100)  # Default pitch
            except:
                pass  # Not all engines support pitch
            
            # Try to find a natural English female voice
            voices = engine.getProperty('voices')
            english_voice_found = False
            
            print(f"🔊 Available voices: {[v.name for v in voices]}")
            
            # Priority 1: Great Britain English female voices
            for voice in voices:
                voice_name = voice.name.lower()
                if ('great britain' in voice_name or 'uk' in voice_name or 'british' in voice_name) and any(indicator in voice_name for indicator in ['female', 'zira', 'susan', 'karen', 'hazel', 'girl']):
                    engine.setProperty('voice', voice.id)
                    english_voice_found = True
                    print(f"🔊 Using Great Britain female voice: {voice.name}")
                    break
            
            # Priority 2: Any Great Britain English voice
            if not english_voice_found:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if 'great britain' in voice_name or 'uk' in voice_name or 'british' in voice_name:
                        engine.setProperty('voice', voice.id)
                        english_voice_found = True
                        print(f"🔊 Using Great Britain voice: {voice.name}")
                        break
            
            # Priority 3: Other English female voices
            if not english_voice_found:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if ('english' in voice_name or 'en_' in voice_name) and any(indicator in voice_name for indicator in ['female', 'zira', 'susan', 'karen', 'hazel', 'girl']):
                        engine.setProperty('voice', voice.id)
                        english_voice_found = True
                        print(f"🔊 Using English female voice: {voice.name}")
                        break
            
            # Priority 4: Any other English voice
            if not english_voice_found:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if 'english' in voice_name or 'en_' in voice_name or 'us' in voice_name:
                        engine.setProperty('voice', voice.id)
                        english_voice_found = True
                        print(f"🔊 Using English voice: {voice.name}")
                        break
            
            # Priority 5: Default to first voice
            if not english_voice_found:
                engine.setProperty('voice', voices[0].id)
                print(f"🔊 Using default voice: {voices[0].name}")
            
            # Split long text into sentences for better pacing
            sentences = text.split('. ')
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    print(f"🔊 Sentence {i+1}: {sentence.strip()}")
                    engine.say(sentence.strip())
                    engine.runAndWait()
                    # Pause between sentences for kids to process
                    if i < len(sentences) - 1:
                        time.sleep(QuizConfig.SENTENCE_PAUSE_TIME)  # Pause between sentences
            
            # Clean up engine properly
            del engine
            return True
            
        except Exception as e:
            print(f"pyttsx3 error: {e}")
            return False
    
    def speak_espeak(self, text):
        """Use espeak for TTS"""
        try:
            # Kid-friendly espeak settings
            cmd = [
                'espeak',
                '-s', '140',  # Slower speed (default 175)
                '-v', 'en+f3',  # Female voice variant
                '-a', '150',   # Amplitude/loudness
                text
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception as e:
            print(f"espeak error: {e}")
            return False
    
    def speak_gtts(self, text):
        """Use Google TTS (requires internet)"""
        try:
            from gtts import gTTS
            import pygame
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tts = gTTS(text=text, lang='en', slow=True)  # Slower for kids
                tts.save(tmp_file.name)
                
                # Play with pygame
                pygame.mixer.init()
                pygame.mixer.music.load(tmp_file.name)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.quit()
                
                # Clean up
                os.unlink(tmp_file.name)
                return True
                
        except Exception as e:
            print(f"gTTS error: {e}")
            return False
    
    def test_tts(self):
        """Test the TTS engine"""
        test_text = "Hello! I'm your quiz master. Are you ready to learn?"
        print(f"Testing TTS with: {test_text}")
        return self.speak(test_text)
