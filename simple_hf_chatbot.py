import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SimpleHuggingFaceChatbot:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.conversation_history = []
        
        # Using simple text completion approach
        self.base_url = "https://api-inference.huggingface.co/models"
        self.current_model = "gpt2"  # Most reliable basic model
        
    def web_search(self, query):
        """Simple web search using DuckDuckGo"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            result = ""
            if data.get('Abstract'):
                result = f"Info: {data['Abstract'][:200]}..."
            
            return result if result else None
            
        except Exception as e:
            return None
    
    def simple_chat(self, user_message):
        """Very simple chat using direct text completion"""
        if not self.api_key:
            return "❌ Please set your HUGGINGFACE_API_KEY in the .env file"
        
        # Check for search request
        search_terms = ['what is', 'who is', 'tell me about', 'search for']
        needs_search = any(term in user_message.lower() for term in search_terms)
        
        context = ""
        if needs_search:
            print("🔍 Searching...")
            search_result = self.web_search(user_message)
            if search_result:
                context = f" {search_result}"
        
        # Create a simple conversational prompt
        recent_context = ""
        if len(self.conversation_history) > 0:
            recent_context = f"Previous: {self.conversation_history[-1]['content'][:50]}... "
        
        # Simple completion prompt
        prompt = f"Human: {user_message}{context}\nAI:"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.8,
                "return_full_text": False,
                "stop": ["Human:", "\\n\\nHuman:"]
            }
        }
        
        try:
            print("🤖 Thinking...")
            response = requests.post(
                f"{self.base_url}/{self.current_model}", 
                headers=headers, 
                json=payload, 
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '').strip()
                    if text:
                        # Clean up response
                        text = text.replace('AI:', '').strip()
                        text = text.split('Human:')[0].strip()  # Remove any leaked human text
                        
                        # Save to history
                        self.conversation_history.append({"role": "user", "content": user_message})
                        self.conversation_history.append({"role": "assistant", "content": text})
                        
                        # Keep history manageable
                        if len(self.conversation_history) > 10:
                            self.conversation_history = self.conversation_history[-6:]
                        
                        return text
                    
            elif response.status_code == 503:
                return "⏳ The AI model is starting up. Please wait a moment and try again."
            elif response.status_code == 429:
                return "⏳ Too many requests. Please wait a moment and try again."
            else:
                return f"⚠️ Service temporarily unavailable (Status: {response.status_code}). Try again in a moment."
                
        except requests.exceptions.Timeout:
            return "⏳ Request timed out. The model might be busy. Please try again."
        except Exception as e:
            return f"❌ Connection error: {str(e)[:100]}"
        
        return "❌ Could not generate response. Please try again."
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation cleared!")

def main():
    print("🤖 Simple & Reliable Hugging Face Chatbot")
    print("=" * 45)
    print("Commands:")
    print("- 'quit' or 'exit': Exit")
    print("- 'clear': Clear conversation")
    print("=" * 45)
    
    chatbot = SimpleHuggingFaceChatbot()
    
    if not chatbot.api_key:
        print("❌ Please add your HUGGINGFACE_API_KEY to the .env file")
        return
    
    print("✅ Ready! Ask me anything or request web searches!")
    print("💡 Try: 'What is Python?' or 'Tell me about AI'")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                chatbot.clear_history()
                continue
            
            elif not user_input:
                continue
            
            # Get response
            response = chatbot.simple_chat(user_input)
            print(f"\n🤖 AI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
