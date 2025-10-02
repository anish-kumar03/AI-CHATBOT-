import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

class HuggingFaceHubChatbot:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.conversation_history = []
        
        if not self.api_key:
            print("❌ Please set HUGGINGFACE_API_KEY in .env file")
            return
        
        # Initialize the Inference Client
        self.client = InferenceClient(token=self.api_key)
        
        # Available models (these should work with the Hub client)
        self.models = {
            "microsoft/DialoGPT-medium": "Conversational AI",
            "google/flan-t5-base": "Text-to-text generation", 
            "microsoft/DialoGPT-small": "Smaller conversational model",
            "EleutherAI/gpt-neo-125M": "Small GPT-style model"
        }
        
        self.current_model = "microsoft/DialoGPT-medium"
    
    def web_search(self, query):
        """Simple web search using DuckDuckGo"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            result = ""
            if data.get('Abstract'):
                result = f"Search result: {data['Abstract'][:300]}..."
            
            return result if result else None
            
        except Exception as e:
            return None
    
    def chat_with_model(self, message, include_search=False):
        """Chat using Hugging Face Hub client"""
        
        if not self.api_key:
            return "❌ Please set your HUGGINGFACE_API_KEY in the .env file"
        
        # Check for search request
        search_context = ""
        if include_search or any(term in message.lower() for term in ['what is', 'who is', 'tell me about']):
            print("🔍 Searching for additional context...")
            search_result = self.web_search(message)
            if search_result:
                search_context = f"\nContext: {search_result}\n"
        
        try:
            # Try text generation first
            full_prompt = f"{search_context}Human: {message}\nAssistant:"
            
            print(f"🤖 Using model: {self.current_model}")
            print("🔄 Generating response...")
            
            # Use the inference client
            response = self.client.text_generation(
                prompt=full_prompt,
                model=self.current_model,
                max_new_tokens=150,
                temperature=0.7,
                return_full_text=False,
                stop_sequences=["Human:", "\nHuman:"]
            )
            
            if response:
                # Clean up the response
                clean_response = response.strip()
                clean_response = clean_response.replace("Assistant:", "").strip()
                
                # Add to history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": clean_response})
                
                # Keep history manageable
                if len(self.conversation_history) > 8:
                    self.conversation_history = self.conversation_history[-6:]
                
                return clean_response
            else:
                return "❌ Empty response from model"
                
        except Exception as e:
            error_msg = str(e)
            
            if "503" in error_msg or "loading" in error_msg.lower():
                return "⏳ The AI model is starting up. Please wait 30-60 seconds and try again."
            elif "429" in error_msg or "rate" in error_msg.lower():
                return "⏳ Too many requests. Please wait a moment and try again."
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                return "❌ API key issue. Please check your HUGGINGFACE_API_KEY."
            else:
                return f"❌ Error: {error_msg[:100]}... Please try again or try a different model."
    
    def switch_model(self, model_key):
        """Switch to a different model"""
        if model_key in self.models:
            self.current_model = model_key
            print(f"✅ Switched to: {model_key}")
        else:
            print("Available models:")
            for key, desc in self.models.items():
                print(f"  - {key}: {desc}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation cleared!")

def main():
    print("🤖 Hugging Face Hub Chatbot")
    print("=" * 35)
    print("Commands:")
    print("- 'quit' or 'exit': Exit")
    print("- 'clear': Clear conversation")
    print("- 'models': Show available models")
    print("- 'search [query]': Force web search")
    print("=" * 35)
    
    chatbot = HuggingFaceHubChatbot()
    
    if not chatbot.api_key:
        return
    
    print("✅ Ready! This uses the Hugging Face Hub client for better reliability.")
    print("💡 Try asking: 'Hello, how are you?' or 'What is Python programming?'")
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
                
            elif user_input.lower() == 'models':
                chatbot.switch_model('')  # This will show available models
                continue
            
            elif user_input.lower().startswith('search '):
                query = user_input[7:]  # Remove 'search ' prefix
                response = chatbot.chat_with_model(query, include_search=True)
                print(f"\n🤖 AI: {response}\n")
                continue
            
            elif not user_input:
                continue
            
            # Get response
            response = chatbot.chat_with_model(user_input)
            print(f"\n🤖 AI: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
