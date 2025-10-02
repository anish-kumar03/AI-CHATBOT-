import openai
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class EnhancedChatbot:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history = []
    
    def web_search(self, query, num_results=3):
        """
        Simple web search using DuckDuckGo Instant Answer API
        This is free and doesn't require API keys
        """
        try:
            # DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            search_results = []
            
            # Get abstract if available
            if data.get('Abstract'):
                search_results.append({
                    'title': data.get('AbstractSource', 'Web Search'),
                    'content': data['Abstract'],
                    'url': data.get('AbstractURL', '')
                })
            
            # Get related topics
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
    
    def get_enhanced_response(self, question):
        """Get response enhanced with web search results"""
        
        # Check if question might benefit from current information
        current_keywords = ['latest', 'recent', 'current', 'today', '2025', 'now', 'current date']
        needs_current_info = any(keyword in question.lower() for keyword in current_keywords)
        
        context_info = None
        if needs_current_info:
            print("Searching the web for current information...")
            context_info = self.web_search(question)
        
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system", 
                "content": f"""You are a helpful assistant that provides accurate factual information. 
                Current date: 2025-08-08. Be honest about your knowledge limitations and suggest checking 
                recent sources for very current events. If provided with web search context, use it to 
                enhance your response while being transparent about your sources."""
            }
        ]
        
        # Add web search context if available
        if context_info:
            context_text = "Here's some current information I found:\n\n"
            for i, result in enumerate(context_info, 1):
                context_text += f"{i}. {result['title']}: {result['content']}\n"
                if result.get('url'):
                    context_text += f"   Source: {result['url']}\n"
                context_text += "\n"
            
            messages.append({"role": "system", "content": context_text})
        
        messages.append({"role": "user", "content": question})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            
            # Store conversation
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'answer': answer,
                'had_web_context': context_info is not None
            })
            
            return answer, context_info
            
        except Exception as e:
            return f"Error getting response: {str(e)}", None

def main():
    chatbot = EnhancedChatbot()
    
    print("🤖 Enhanced Factual Chatbot")
    print("Ask me anything! I can search the web for current information when needed.")
    print("Commands: 'quit' to exit, 'history' to see recent questions\n")
    
    while True:
        question = input("Your question: ")
        
        if question.lower() in ['quit', 'exit']:
            break
        elif question.lower() == 'history':
            print("\n📝 Recent Questions:")
            for i, item in enumerate(chatbot.conversation_history[-5:], 1):
                print(f"{i}. {item['question'][:60]}...")
            print()
            continue
        
        answer, context = chatbot.get_enhanced_response(question)
        print(f"\n💡 Answer: {answer}")
        
        if context:
            print(f"\n🔍 Sources used: {len(context)} web results")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()