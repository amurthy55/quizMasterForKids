import os
import openai
from quiz_config import QuizConfig
from context_manager import ContextManager

class OpenAIClient:
    def __init__(self):
        self.client = None
        self.context_manager = ContextManager()
        self.setup_client()
    
    def setup_client(self):
        """Setup OpenAI client"""
        api_key = QuizConfig.OPENAI_API_KEY
        if api_key == "your-api-key-here":
            print("Warning: Please set OPENAI_API_KEY environment variable")
            print("Example: export OPENAI_API_KEY='your-actual-api-key'")
            return False
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
            return True
        except Exception as e:
            print(f"Error setting up OpenAI client: {e}")
            return False
    
    def chat_with_context(self, user_input):
        """Send user input to OpenAI with conversation context"""
        if not self.client:
            return "Sorry, I'm having trouble connecting to my brain. Please check the API key."
        
        try:
            # Add user message to context
            self.context_manager.add_message("user", user_input)
            
            # Get conversation history
            messages = self.context_manager.get_conversation_history()
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using cheaper model for economy
                messages=messages,
                max_tokens=100,  # Keep responses short for kids
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Add assistant response to context
            self.context_manager.add_message("assistant", assistant_response)
            
            return assistant_response
            
        except Exception as e:
            error_msg = f"Oops! Something went wrong: {str(e)}"
            print(f"OpenAI API Error: {e}")
            return error_msg
    
    def get_session_info(self):
        """Get current session information"""
        return self.context_manager.get_session_info()
    
    def clear_session(self):
        """Clear current conversation session"""
        self.context_manager.clear_context()
        return "Session cleared! Let's start fresh!"
