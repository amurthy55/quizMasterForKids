import json
import os
import random
from datetime import datetime

class JsonQuizManager:
    def __init__(self):
        self.quiz_data_dir = "quiz_data"
        self.current_topic = None
        self.current_questions = []
        self.asked_questions = set()
        self.question_history = []
        
        # Load available topics
        self.available_topics = self.load_available_topics()
    
    def load_available_topics(self):
        """Load all available quiz topics from JSON files"""
        topics = {}
        if not os.path.exists(self.quiz_data_dir):
            return topics
        
        for filename in os.listdir(self.quiz_data_dir):
            if filename.endswith('.json'):
                topic_name = filename.replace('.json', '')
                file_path = os.path.join(self.quiz_data_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        topics[topic_name] = data
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return topics
    
    def get_available_topic_names(self):
        """Get list of available topic names"""
        return list(self.available_topics.keys())
    
    def select_topic(self, topic_name):
        """Select a topic and load its questions"""
        topic_name = topic_name.lower().replace(' ', '_').replace('_', ' ')
        if topic_name in self.available_topics:
            self.current_topic = topic_name
            self.current_questions = self.available_topics[topic_name]['questions']
            return True
        else:
            # Try to find similar topic with flexible matching
            available = self.get_available_topic_names()
            for topic in available:
                # Remove underscores and spaces for comparison
                clean_topic = topic.lower().replace('_', ' ')
                clean_input = topic_name.replace('_', ' ')
                
                # Check for partial matches
                if (clean_topic in clean_input or 
                    clean_input in clean_topic or
                    clean_topic.split()[0] in clean_input or
                    clean_input.split()[0] in clean_topic):
                    self.current_topic = topic
                    self.current_questions = self.available_topics[topic]['questions']
                    return True
            return False
    
    def get_random_question(self):
        """Get a random question that hasn't been asked yet"""
        if not self.current_questions:
            return None
        
        # Filter out already asked questions
        available_questions = [
            q for q in self.current_questions 
            if q['id'] not in self.asked_questions
        ]
        
        # If all questions have been asked, reset the asked questions
        if not available_questions:
            self.asked_questions.clear()
            available_questions = self.current_questions
        
        # Select random question
        question = random.choice(available_questions)
        self.asked_questions.add(question['id'])
        
        # Add to history
        self.question_history.append({
            'timestamp': datetime.now().isoformat(),
            'topic': self.current_topic,
            'question_id': question['id'],
            'question': question['question'],
            'answer': question['answer']
        })
        
        return question
    
    def verify_answer(self, question, user_answer):
        """Verify if the user's answer is correct"""
        correct_answer = str(question['answer']).lower().strip()
        user_answer = user_answer.lower().strip()
        
        # Handle spelling bee - remove spaces and check letters
        if 'spell the word' in question['question'].lower():
            # Remove spaces from user's spelled answer
            user_letters = user_answer.replace(' ', '').replace('-', '')
            
            if user_letters == correct_answer:
                return True, "Correct! Well done!"
            elif user_letters in correct_answer or correct_answer in user_letters:
                return True, "Correct! Well done!"
        
        # Handle math answers - convert both to strings and compare
        if correct_answer.isdigit():
            # Extract numbers from user answer
            import re
            numbers_in_answer = re.findall(r'\d+', user_answer)
            if numbers_in_answer and numbers_in_answer[0] == correct_answer:
                return True, "Correct! Well done!"
            # Also check if user said the number directly
            if user_answer == correct_answer:
                return True, "Correct! Well done!"
        
        # Handle multiple choice or partial matches
        if correct_answer == user_answer:
            return True, "Correct! Well done!"
        
        # Check if answer contains the correct word
        if correct_answer in user_answer or user_answer in correct_answer:
            return True, "Correct! Well done!"
        
        # For spelling bee, spell out the correct answer
        if 'spell the word' in question['question'].lower():
            spelled_answer = ' '.join(list(question['answer'].upper()))
            return False, f"Not quite. The correct answer is spelled: {spelled_answer}."
        
        return False, f"Not quite. The correct answer is {question['answer']}."
    
    def get_hint(self, question, hint_level=1):
        """Get a hint for the question"""
        hints = question.get('hints', [])
        if hints and hint_level <= len(hints):
            return hints[hint_level - 1]
        return "No more hints available."
    
    def get_explanation(self, question):
        """Get explanation for the answer"""
        return question.get('explanation', 'No explanation available.')
    
    def reset_topic(self):
        """Reset the current topic and asked questions"""
        self.current_topic = None
        self.current_questions = []
        self.asked_questions.clear()
    
    def get_question_history(self, limit=10):
        """Get recent question history"""
        return self.question_history[-limit:]
    
    def get_stats(self):
        """Get quiz statistics"""
        total_questions = len(self.current_questions) if self.current_questions else 0
        asked_count = len(self.asked_questions)
        remaining = total_questions - asked_count
        
        return {
            'current_topic': self.current_topic,
            'total_questions': total_questions,
            'asked_questions': asked_count,
            'remaining_questions': remaining,
            'history_count': len(self.question_history)
        }
