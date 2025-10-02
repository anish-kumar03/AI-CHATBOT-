import openai
import requests
import wikipedia
import json
from datetime import datetime
import re

class AdvancedFactualChatbot:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.conversation_history = []
    
    def search_wikipedia(self, query, sentences=3):
        """Search Wikipedia for factual information"""
        try:
            # Search for the topic
            search_results = wikipedia.search(query, results=1)
            if search_results:
                page = wikipedia.page(search_results[0])
                summary = wikipedia.summary(search_results[0], sentences=sentences)
                return {
                    'source': 'Wikipedia',
                    'title': page.title,
                    'content': summary,
                    'url': page.url
                }
        except Exception as e:
            return None
    
    def get_news_info(self, query):
        """Get recent news information (requires News API key)"""
        try:
            # You'll need to get a free API key from newsapi.org
            news_api_key = os.getenv('NEWS_API_KEY')
            if not news_api_key:
                return None
            
            url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={news_api_key}"
            response = requests.get(url)
            data = response.json()
            
            if data['status'] == 'ok' and data['articles']:
                article = data['articles'][0]  # Get the most recent article
                return {
                    'source': 'News API',
                    'title': article['title'],
                    'content': article['description'],
                    'url': article['url'],
                    'published': article['publishedAt']
                }
        except Exception as e:
            return None
    
    def get_ai_response(self, question, context_info=None):
        """Get response from AI with optional context"""
        system_message = """You are a helpful assistant that provides accurate factual information. 
        When provided with context from reliable sources, use it to enhance your response. 
        Always be honest about the limitations of your knowledge and suggest checking recent sources for time-sensitive information."""
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add context if available
        if context_info:
            context_text = f"Here's some relevant information from {context_info['source']}:\n"
            context_text += f"Title: {context_info['title']}\n"
            context_text += f"Content: {context_info['content']}\n"
            if 'url' in context_info:
                context_text += f"Source URL: {context_info['url']}\n"
            
            messages.append({"role": "system", "content": context_text})
        
        messages.append({"role": "user", "content": question})
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI service unavailable: {str(e)}"
    
    def answer_question(self, question):
        """Main method to answer questions using multiple sources"""
        print("Searching for information...")
        
        # Try to get information from Wikipedia
        wiki_info = self.search_wikipedia(question)
        
        # Try to get recent news if the question seems time-sensitive
        time_sensitive_keywords = ['recent', 'latest', 'current', 'today', 'news', '2023', '2024']
        if any(keyword in question.lower() for keyword in time_sensitive_keywords):
            news_info = self.get_news_info(question)
        else:
            news_info = None
        
        # Choose the best context source
        context_info = news_info if news_info else wiki_info
        
        # Get AI response with context
        response = self.get_ai_response(question, context_info)
        
        # Store in conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response,
            'context_source': context_info['source'] if context_info else None
        })
        
        return response, context_info

# Example usage
if __name__ == "__main__":
    chatbot = AdvancedFactualChatbot()
    
    print("Advanced Factual Chatbot - Ask me anything!")
    print("Type 'quit' to exit, 'history' to see conversation history\n")
    
    while True:
        question = input("Your question: ")
        
        if question.lower() == 'quit':
            break
        elif question.lower() == 'history':
            for i, entry in enumerate(chatbot.conversation_history[-5:], 1):
                print(f"{i}. Q: {entry['question'][:50]}...")
                print(f"   A: {entry['response'][:100]}...\n")
            continue
        
        answer, context = chatbot.answer_question(question)
        print(f"\nAnswer: {answer}")
        
        if context:
            print(f"\nSource: {context['source']} - {context['title']}")
            if 'url' in context:
                print(f"Reference: {context['url']}")
        
        print("\n" + "="*50 + "\n")