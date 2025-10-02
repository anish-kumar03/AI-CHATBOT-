import os
import requests
import json
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiChatbot:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.conversation_history = []
        
        if not self.gemini_api_key or self.gemini_api_key == 'your_gemini_api_key_here':
            print("❌ Please set your GEMINI_API_KEY in the .env file")
            print("Get one from: https://makersuite.google.com/app/apikey")
            return
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        
        # Available Gemini models
        self.models = {
            'gemini-pro': 'Best for text generation and conversations',
            'gemini-1.5-pro': 'Latest model with enhanced capabilities',
            'gemini-1.5-flash': 'Fastest model for quick responses'
        }
        
        # Default to the fastest model
        self.current_model = 'gemini-1.5-flash'
        
        try:
            self.model = genai.GenerativeModel(self.current_model)
            print(f"✅ Gemini API initialized successfully with {self.current_model}")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.model = None
    
    def web_search(self, query):
        """Enhanced web search using DuckDuckGo"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            results = []
            
            # Get the main abstract/definition
            if data.get('Abstract'):
                results.append(f"Search Result: {data['Abstract']}")
            
            # Get answer if available
            if data.get('Answer'):
                results.append(f"Quick Answer: {data['Answer']}")
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:3]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append(f"Related: {topic['Text'][:150]}...")
            
            return "\n".join(results) if results else None
            
        except Exception as e:
            print(f"Search error: {e}")
            return None
    
    def switch_model(self, model_name):
        """Switch between different Gemini models"""
        if model_name in self.models:
            try:
                self.current_model = model_name
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ Switched to {model_name}")
                return True
            except Exception as e:
                print(f"❌ Failed to switch to {model_name}: {e}")
                return False
        else:
            print("Available models:")
            for model, desc in self.models.items():
                print(f"  • {model}: {desc}")
            return False
    
    def chat(self, user_message, include_search=False):
        """Main chat function using Gemini"""
        
        if not self.model:
            return "❌ Gemini model not initialized. Please check your API key."
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Check for search request or questions that might need current info
        search_context = ""
        search_triggers = ['current', 'latest', 'recent', 'today', 'news', 'what is', 'who is', 'tell me about']
        
        if include_search or any(trigger in user_message.lower() for trigger in search_triggers):
            print("🔍 Searching for current information...")
            search_result = self.web_search(user_message)
            if search_result:
                search_context = f"\n\nCurrent Information:\n{search_result}\n"
                print("✅ Found additional context!")
        
        # Prepare conversation context
        conversation_context = ""
        if len(self.conversation_history) > 1:
            for msg in self.conversation_history[-4:]:  # Last 4 messages for context
                conversation_context += f"{msg['role']}: {msg['content']}\n"
        
        # Create the full prompt
        full_prompt = f"""You are a helpful, knowledgeable AI assistant. Provide accurate, informative, and conversational responses.

{search_context}

{conversation_context}

Please respond to the user's message in a helpful and engaging way."""
        
        try:
            print("🤖 Gemini is thinking...")
            
            # Generate response using Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=1000,
                    temperature=0.7
                )
            )
            
            if response.text:
                bot_response = response.text.strip()
                
                # Add to conversation history
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep conversation history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-10:]
                
                return bot_response
            else:
                return "❌ Sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "⏳ API quota exceeded. Please wait a moment and try again, or check your API usage."
            elif "api" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API key issue. Please check your GEMINI_API_KEY in the .env file."
            else:
                return f"❌ Error: {error_msg}. Please try again."
    
    def get_conversation_stats(self):
        """Get conversation statistics"""
        return {
            "current_model": self.current_model,
            "messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m["role"] == "assistant"])
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation history cleared!")

def test_gemini_connection():
    """Test if Gemini API is working"""
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not found or not set")
        print("Please add your Gemini API key to the .env file")
        print("Get one from: https://makersuite.google.com/app/apikey")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test.")
        
        if response.text:
            print(f"✅ Gemini API working! Test response: {response.text[:50]}...")
            return True
        else:
            print("❌ Gemini API not responding properly")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    print("🚀 Gemini-Powered AI Chatbot")
    print("=" * 40)
    print("Features:")
    print("✅ Google Gemini AI (Fast & Reliable)")
    print("✅ Web search integration")
    print("✅ Smart conversation memory")
    print("✅ Multiple model options")
    print("=" * 40)
    print("Commands:")
    print("- 'quit' or 'exit': Exit the chat")
    print("- 'clear': Clear conversation history")
    print("- 'search [query]': Force web search")
    print("- 'models': Show available models")
    print("- 'switch [model]': Switch Gemini model")
    print("- 'stats': Show conversation stats")
    print("=" * 40)
    
    # Test connection first
    if not test_gemini_connection():
        return
    
    chatbot = GeminiChatbot()
    
    if not chatbot.model:
        return
    
    print("✅ Ready! Gemini AI is faster and more intelligent than previous versions!")
    print("💡 Try asking:")
    print("   • 'Tell me about the latest AI developments'")
    print("   • 'Suggest some good movies to watch'")
    print("   • 'Explain quantum computing in simple terms'")
    print("   • 'Write a Python function to sort a list'")
    print("   • 'What are the current trends in technology?'")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using Gemini Chatbot! Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                chatbot.clear_history()
                continue
                
            elif user_input.lower().startswith('search '):
                query = user_input[7:]  # Remove 'search ' prefix
                response = chatbot.chat(query, include_search=True)
                print(f"\n🤖 Gemini: {response}\n")
                continue
            
            elif user_input.lower() == 'models':
                print("Available Gemini models:")
                for model, desc in chatbot.models.items():
                    indicator = " (current)" if model == chatbot.current_model else ""
                    print(f"  • {model}: {desc}{indicator}")
                continue
            
            elif user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                chatbot.switch_model(model_name)
                continue
            
            elif user_input.lower() == 'stats':
                stats = chatbot.get_conversation_stats()
                print(f"📊 Conversation Stats:")
                print(f"   Current model: {stats['current_model']}")
                print(f"   Total messages: {stats['messages']}")
                print(f"   Your messages: {stats['user_messages']}")
                print(f"   AI responses: {stats['assistant_messages']}")
                continue
            
            elif not user_input:
                continue
            
            # Get chatbot response
            response = chatbot.chat(user_input)
            print(f"\n🤖 Gemini: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
