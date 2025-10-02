import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class HuggingFaceChatbot:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.conversation_history = []
        
        # Free models you can use with Hugging Face
        self.model_options = {
            'llama': 'meta-llama/Llama-2-7b-chat-hf',
            'mistral': 'mistralai/Mistral-7B-Instruct-v0.1',
            'falcon': 'tiiuae/falcon-7b-instruct',
            'code_llama': 'codellama/CodeLlama-7b-Instruct-hf',
            'zephyr': 'HuggingFaceH4/zephyr-7b-beta'  # Great general purpose model
        }
        
        # Default to Zephyr as it's well-balanced for conversations
        self.current_model = self.model_options['zephyr']
        self.base_url = "https://api-inference.huggingface.co/models"
    
    def web_search(self, query, num_results=3):
        """
        Simple web search using DuckDuckGo Instant Answer API
        This is free and doesn't require API keys
        """
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
    
    def switch_model(self, model_name):
        """Switch between different Hugging Face models"""
        if model_name in self.model_options:
            self.current_model = self.model_options[model_name]
            print(f"Switched to model: {model_name}")
        else:
            print(f"Available models: {list(self.model_options.keys())}")
    
    def query_huggingface(self, payload):
        """Send request to Hugging Face API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{self.current_model}"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"API request failed: {e}")
            return None
    
    def chat(self, user_message):
        """Main chat function"""
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
            else:
                print("❌ No search results found")
        
        # Prepare the prompt for Hugging Face
        conversation = ""
        for msg in self.conversation_history[-5:]:  # Last 5 messages for context
            conversation += f"{msg['role']}: {msg['content']}\n"
        
        if context:
            conversation += f"\nAdditional Context: {context}\n"
        
        prompt = f"""<|system|>
You are a helpful, friendly AI assistant. Provide accurate, informative, and conversational responses.
</s>
<|user|>
{conversation}
</s>
<|assistant|>
"""
        
        # Query Hugging Face API
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        print("🤖 Generating response...")
        response = self.query_huggingface(payload)
        
        if response and isinstance(response, list) and len(response) > 0:
            bot_response = response[0].get('generated_text', '').strip()
            
            # Clean up the response
            if bot_response:
                # Remove any system tokens that might leak through
                bot_response = bot_response.replace('<|system|>', '').replace('<|user|>', '').replace('<|assistant|>', '').replace('</s>', '').strip()
                
                # Add to conversation history
                self.conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep conversation history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-10:]
                
                return bot_response
            else:
                return "I apologize, but I couldn't generate a proper response. Please try again."
        else:
            return "❌ Sorry, I'm having trouble connecting to the AI model. This might be due to high demand. Please try again in a moment."
    
    def get_model_info(self):
        """Get information about current model"""
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
    print("🤖 Hugging Face Chatbot (Free OpenAI Alternative)")
    print("=" * 50)
    print("Available commands:")
    print("- 'quit' or 'exit': Exit the chatbot")
    print("- 'clear': Clear conversation history")
    print("- 'models': Show available models")
    print("- 'switch [model_name]': Switch to a different model")
    print("- 'info': Show current model information")
    print("=" * 50)
    
    chatbot = HuggingFaceChatbot()
    
    # Check if API key is set
    if not chatbot.api_key or chatbot.api_key == 'your_huggingface_api_key_here':
        print("❌ Please set your HUGGINGFACE_API_KEY in the .env file")
        print("You can get a free API key from: https://huggingface.co/settings/tokens")
        return
    
    print(f"✅ Using model: {chatbot.current_model}")
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
            
            elif user_input.lower() == 'models':
                print("Available models:", list(chatbot.model_options.keys()))
                continue
            
            elif user_input.lower().startswith('switch '):
                model_name = user_input[7:].strip()
                chatbot.switch_model(model_name)
                continue
            
            elif user_input.lower() == 'info':
                info = chatbot.get_model_info()
                print(f"Current model: {info['current_model']}")
                print(f"Available models: {info['available_models']}")
                print(f"Conversation length: {info['conversation_length']} messages")
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
