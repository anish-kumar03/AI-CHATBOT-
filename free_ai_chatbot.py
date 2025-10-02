import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class FreeAIChatbot:
    def __init__(self):
        self.conversation_history = []
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        
    def web_search(self, query):
        """Enhanced web search using DuckDuckGo"""
        try:
            # DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=8)
            data = response.json()
            
            results = []
            
            # Get the main abstract/definition
            if data.get('Abstract'):
                results.append(f"Definition: {data['Abstract']}")
            
            # Get answer if available
            if data.get('Answer'):
                results.append(f"Answer: {data['Answer']}")
            
            # Get related topics
            for topic in data.get('RelatedTopics', [])[:2]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append(f"Info: {topic['Text'][:150]}...")
            
            return "\n".join(results) if results else None
            
        except Exception as e:
            print(f"Search error: {e}")
            return None
    
    def generate_smart_response(self, user_message, search_context=""):
        """Generate response using rule-based approach with search context"""
        
        message_lower = user_message.lower()
        
        # Handle greetings
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm your AI assistant. I can answer questions, provide information through web search, and have conversations with you. What would you like to know?"
        
        # Handle questions about the assistant
        if any(phrase in message_lower for phrase in ['who are you', 'what are you', 'about you']):
            return "I'm a free AI assistant powered by web search and smart response generation. I can help you find information, answer questions, and chat with you!"
        
        # Handle requests for information/search
        search_triggers = ['what is', 'who is', 'tell me about', 'explain', 'define', 'information about']
        if any(trigger in message_lower for trigger in search_triggers) or search_context:
            if search_context:
                return f"Based on my search, here's what I found:\n\n{search_context}\n\nWould you like me to search for more specific information about any aspect of this topic?"
            else:
                return "I'd be happy to help you find information about that topic. Let me search for you."
        
        # Handle how-to questions
        if message_lower.startswith('how to') or message_lower.startswith('how do'):
            return f"That's a great question about '{user_message}'. Let me search for step-by-step information to help you with this."
        
        # Handle math questions (simple ones)
        if any(word in message_lower for word in ['calculate', 'math', '+', '-', '*', '/', 'equals']):
            try:
                # Very basic math evaluation (be careful with eval!)
                import re
                if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', user_message.replace('what is', '').replace('calculate', '').strip()):
                    expression = user_message.replace('what is', '').replace('calculate', '').strip()
                    result = eval(expression)
                    return f"The answer is: {result}"
            except:
                pass
            return "I can help with basic math. Try asking something like 'what is 15 + 25' or 'calculate 10 * 5'."
        
        # Handle programming questions
        if any(word in message_lower for word in ['python', 'programming', 'code', 'function', 'variable']):
            if search_context:
                return f"Here's what I found about programming:\n\n{search_context}\n\nWould you like me to search for more specific programming examples or tutorials?"
            else:
                return "I'd be happy to help with programming questions! Let me search for relevant information."
        
        # Handle general conversation
        conversation_starters = ['tell me', 'i want to know', 'can you help', 'i need help']
        if any(starter in message_lower for starter in conversation_starters):
            return "Of course! I'm here to help. I can search for information on almost any topic, answer questions, or just chat. What specifically would you like to know about?"
        
        # Default response with search offer
        return f"That's an interesting question about '{user_message}'. Let me search for current information on this topic to give you the best answer possible."
    
    def chat(self, user_message):
        """Main chat function"""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Check if this needs a web search
        search_triggers = ['what is', 'who is', 'tell me about', 'explain', 'define', 'how to', 'information about']
        needs_search = any(trigger in user_message.lower() for trigger in search_triggers)
        
        search_context = ""
        if needs_search:
            print("🔍 Searching for information...")
            search_result = self.web_search(user_message)
            if search_result:
                search_context = search_result
                print("✅ Found information!")
            else:
                print("⚠️ No specific search results found")
        
        # Generate response
        response = self.generate_smart_response(user_message, search_context)
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.conversation_history) > 12:
            self.conversation_history = self.conversation_history[-8:]
        
        return response
    
    def get_conversation_stats(self):
        """Get conversation statistics"""
        return {
            "messages": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m["role"] == "assistant"])
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation history cleared!")

def main():
    print("🤖 Free AI Assistant with Web Search")
    print("=" * 40)
    print("This assistant combines smart responses with web search!")
    print("Commands:")
    print("- 'quit' or 'exit': Exit the chat")
    print("- 'clear': Clear conversation history")
    print("- 'stats': Show conversation statistics")
    print("=" * 40)
    
    chatbot = FreeAIChatbot()
    
    print("✅ Ready! I can help with:")
    print("   • General questions and information")
    print("   • Web searches and current info")
    print("   • Programming and tech topics")
    print("   • Math calculations")
    print("   • Casual conversation")
    print()
    print("💡 Try asking:")
    print("   • 'What is Python programming?'")
    print("   • 'Tell me about artificial intelligence'")
    print("   • 'How to learn web development?'")
    print("   • 'What is 25 * 4?'")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for chatting! Goodbye!")
                break
            
            elif user_input.lower() == 'clear':
                chatbot.clear_history()
                continue
                
            elif user_input.lower() == 'stats':
                stats = chatbot.get_conversation_stats()
                print(f"📊 Conversation Stats:")
                print(f"   Total messages: {stats['messages']}")
                print(f"   Your messages: {stats['user_messages']}")
                print(f"   My responses: {stats['assistant_messages']}")
                continue
            
            elif not user_input:
                continue
            
            # Get chatbot response
            print()  # Add space for better readability
            response = chatbot.chat(user_input)
            print(f"\n🤖 Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
