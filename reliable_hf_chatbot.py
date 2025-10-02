import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ImprovedHuggingFaceChatbot:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.conversation_history = []
        
        # More reliable models with fallback options
        self.model_options = {
            'gpt2': 'gpt2',  # Always available, fast
            'distilgpt2': 'distilgpt2',  # Faster alternative
            'microsoft-dialogpt': 'microsoft/DialoGPT-medium',  # Good for conversations
            'google-flan-t5': 'google/flan-t5-base',  # Instruction following
            'facebook-blenderbot': 'facebook/blenderbot-400M-distill'  # Conversation focused
        }
        
        # Start with the most reliable model
        self.current_model = 'gpt2'
        self.base_url = "https://api-inference.huggingface.co/models"
        self.max_retries = 3
        self.retry_delay = 2
    
    def test_model_availability(self, model_key):
        """Test if a specific model is available and responsive"""
        model_name = self.model_options.get(model_key, model_key)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{model_name}"
        test_payload = {
            "inputs": "Hello",
            "parameters": {"max_new_tokens": 5}
        }
        
        try:
            response = requests.post(url, headers=headers, json=test_payload, timeout=10)
            
            if response.status_code == 200:
                return True, "Available"
            elif response.status_code == 503:
                return False, "Model is loading (try again in a moment)"
            elif response.status_code == 429:
                return False, "Rate limited (try again later)"
            else:
                return False, f"Error: {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def find_available_model(self):
        """Find the first available model"""
        print("🔍 Checking model availability...")
        
        for model_key in self.model_options.keys():
            print(f"Testing {model_key}...", end=" ")
            available, status = self.test_model_availability(model_key)
            
            if available:
                print(f"✅ {status}")
                self.current_model = model_key
                return True
            else:
                print(f"❌ {status}")
        
        return False
    
    def web_search(self, query, num_results=3):
        """Simple web search using DuckDuckGo Instant Answer API"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            search_results = []
            
            if data.get('Abstract'):
                search_results.append({
                    'title': data.get('AbstractSource', 'Web Search'),
                    'content': data['Abstract'],
                    'url': data.get('AbstractURL', '')
                })
            
            for topic in data.get('RelatedTopics', [])[:2]:
                if isinstance(topic, dict) and topic.get('Text'):
                    search_results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1],
                        'content': topic['Text'][:200] + '...',
                        'url': topic.get('FirstURL', '')
                    })
            
            return search_results if search_results else None
            
        except Exception as e:
            print(f"Web search error: {e}")
            return None
    
    def query_huggingface_with_retry(self, payload):
        """Send request to Hugging Face API with retry logic"""
        model_name = self.model_options[self.current_model]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{model_name}"
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{self.max_retries}...")
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    print("⏳ Model is loading, waiting...")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                    continue
                elif response.status_code == 429:
                    print("⏳ Rate limited, waiting...")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 2)
                    continue
                else:
                    print(f"❌ API Error: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        print("Trying different model...")
                        if self.find_available_model():
                            continue
                    return None
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                
        return None
    
    def chat(self, user_message):
        """Main chat function with improved error handling"""
        if not self.api_key:
            return "❌ Please set your HUGGINGFACE_API_KEY in the .env file"
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Check if user wants web search
        search_keywords = ['search for', 'look up', 'find information about', 'what is', 'who is']
        needs_search = any(keyword in user_message.lower() for keyword in search_keywords)
        
        context = ""
        if needs_search:
            # Extract search query
            search_query = user_message.lower()
            for keyword in search_keywords:
                if keyword in search_query:
                    search_query = search_query.split(keyword)[-1].strip()
                    break
            
            print(f"🔍 Searching for: {search_query}")
            search_results = self.web_search(search_query)
            
            if search_results:
                context = "\n\nWeb Search Results:\n"
                for i, result in enumerate(search_results, 1):
                    context += f"{i}. {result['title']}: {result['content']}\n"
                print("✅ Found relevant information")
        
        # Prepare conversation context
        conversation = ""
        for msg in self.conversation_history[-3:]:  # Last 3 messages for context
            conversation += f"{msg['role']}: {msg['content']}\n"
        
        if context:
            conversation += f"\nContext: {context}\n"
        
        # Simple prompt that works with basic models
        prompt = f"Complete this conversation naturally:\n{conversation}assistant:"
        
        # Query Hugging Face API
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False,
                "pad_token_id": 50256  # Common pad token
            }
        }
        
        print(f"🤖 Using model: {self.current_model}")
        response = self.query_huggingface_with_retry(payload)
        
        if response:
            if isinstance(response, list) and len(response) > 0:
                bot_response = response[0].get('generated_text', '').strip()
            elif isinstance(response, dict):
                bot_response = response.get('generated_text', '').strip()
            else:
                bot_response = ""
            
            if bot_response:
                # Clean up the response
                bot_response = bot_response.replace('assistant:', '').strip()
                
                # Add to conversation history
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep conversation history manageable
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-6:]
                
                return bot_response
            else:
                return "I apologize, but I couldn't generate a proper response. Please try again."
        else:
            return "❌ All models seem to be unavailable right now. Please try again in a few minutes, or the models might be experiencing high demand."
    
    def get_status(self):
        """Get current status and model information"""
        return {
            'current_model': self.current_model,
            'available_models': list(self.model_options.keys()),
            'conversation_length': len(self.conversation_history)
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation history cleared")

def main():
    print("🤖 Improved Hugging Face Chatbot")
    print("=" * 40)
    print("This version automatically handles connection issues!")
    print("Available commands:")
    print("- 'quit' or 'exit': Exit the chatbot")
    print("- 'clear': Clear conversation history")
    print("- 'status': Show current status")
    print("- 'test': Test model availability")
    print("=" * 40)
    
    chatbot = ImprovedHuggingFaceChatbot()
    
    # Check if API key is set
    if not chatbot.api_key:
        print("❌ Please set your HUGGINGFACE_API_KEY in the .env file")
        return
    
    # Find an available model
    print("🚀 Starting up...")
    if not chatbot.find_available_model():
        print("❌ No models are currently available. Please try again later.")
        return
    
    print(f"✅ Ready! Using model: {chatbot.current_model}")
    print("You can ask questions, request web searches, or just chat!")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                chatbot.clear_history()
                continue
            
            elif user_input.lower() == 'status':
                status = chatbot.get_status()
                print(f"Current model: {status['current_model']}")
                print(f"Available models: {status['available_models']}")
                print(f"Conversation length: {status['conversation_length']} messages")
                continue
            
            elif user_input.lower() == 'test':
                chatbot.find_available_model()
                continue
            
            elif not user_input:
                continue
            
            # Get chatbot response
            response = chatbot.chat(user_input)
            print(f"\n🤖 Bot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()
