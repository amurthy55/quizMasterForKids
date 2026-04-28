import json
import os
from datetime import datetime
from quiz_config import QuizConfig

class ContextManager:
    def __init__(self):
        self.context_file = QuizConfig.get_context_file_path()
        self.context = self.load_context()
    
    def load_context(self):
        """Load conversation context from file"""
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, 'r') as f:
                    return json.load(f)
            except:
                return self.create_new_context()
        else:
            return self.create_new_context()
    
    def create_new_context(self):
        """Create new conversation context"""
        return {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "quiz_topics": [],
            "child_age_range": "6-10 years"
        }
    
    def save_context(self):
        """Save conversation context to file"""
        try:
            with open(self.context_file, 'w') as f:
                json.dump(self.context, f, indent=2)
        except Exception as e:
            print(f"Error saving context: {e}")
    
    def add_message(self, role, content):
        """Add message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.context["messages"].append(message)
        self.save_context()
    
    def get_conversation_history(self, max_messages=10):
        """Get recent conversation history for OpenAI"""
        messages = []
        
        # Add system message
        messages.append({
            "role": "system",
            "content": QuizConfig.SYSTEM_PROMPT
        })
        
        # Add recent conversation (limit to last max_messages)
        recent_messages = self.context["messages"][-max_messages:]
        for msg in recent_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return messages
    
    def clear_context(self):
        """Clear conversation context"""
        self.context = self.create_new_context()
        self.save_context()
    
    def get_session_info(self):
        """Get current session information"""
        return {
            "session_id": self.context["session_id"],
            "started_at": self.context["started_at"],
            "message_count": len(self.context["messages"])
        }
