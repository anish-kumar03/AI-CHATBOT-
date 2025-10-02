import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ImprovedFreeAIChatbot:
    def __init__(self):
        self.conversation_history = []
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        
        # Knowledge base for common topics
        self.knowledge_base = {
            'cars': {
                'info': "Cars are motor vehicles designed for transportation on roads. They typically have four wheels, an engine, and can carry passengers. Modern cars use internal combustion engines or electric motors for power.",
                'details': [
                    "Cars were first invented in the late 1800s",
                    "Popular car brands include Toyota, Ford, Honda, BMW, Mercedes-Benz, and Tesla",
                    "Modern cars can be powered by gasoline, diesel, hybrid systems, or electricity",
                    "Cars have revolutionized transportation and changed how people live and work",
                    "Safety features include airbags, seat belts, ABS brakes, and collision detection"
                ]
            },
            'programming': {
                'info': "Programming is the process of creating computer software using programming languages. It involves writing instructions that computers can execute.",
                'details': [
                    "Popular programming languages include Python, JavaScript, Java, and C++",
                    "Programming involves problem-solving and logical thinking",
                    "Software developers use programming to create apps, websites, and systems",
                    "Programming can be learned through online courses, books, and practice"
                ]
            },
            'artificial intelligence': {
                'info': "Artificial Intelligence (AI) is technology that enables machines to perform tasks that typically require human intelligence.",
                'details': [
                    "AI includes machine learning, natural language processing, and computer vision",
                    "AI is used in smartphones, search engines, recommendations, and autonomous vehicles",
                    "Machine learning allows computers to learn from data without explicit programming",
                    "Popular AI applications include ChatGPT, Siri, Google Assistant, and image recognition"
                ]
            },
            'python': {
                'info': "Python is a high-level programming language known for its simplicity and readability. It's widely used for web development, data science, and AI.",
                'details': [
                    "Created by Guido van Rossum and first released in 1991",
                    "Popular for beginners due to its simple syntax",
                    "Used by companies like Google, Netflix, Instagram, and NASA",
                    "Great for web development, data analysis, machine learning, and automation"
                ]
            }
        }
        
        # Entertainment recommendations database
        self.entertainment_db = {
            'movies': {
                'action': ["John Wick", "Mad Max: Fury Road", "The Dark Knight", "Mission Impossible", "Avengers: Endgame"],
                'comedy': ["The Grand Budapest Hotel", "Superbad", "Knives Out", "The Hangover", "Deadpool"],
                'drama': ["The Shawshank Redemption", "Forrest Gump", "The Godfather", "Schindler's List", "12 Years a Slave"],
                'sci-fi': ["Inception", "Interstellar", "Blade Runner 2049", "The Matrix", "Dune"],
                'horror': ["Get Out", "A Quiet Place", "Hereditary", "The Conjuring", "It"],
                'animated': ["Spider-Man: Into the Spider-Verse", "Toy Story", "Your Name", "Spirited Away", "Coco"],
                'recent': ["Top Gun: Maverick", "Everything Everywhere All at Once", "The Batman", "Dune", "No Way Home"]
            },
            'books': {
                'fiction': ["1984", "To Kill a Mockingbird", "Pride and Prejudice", "The Great Gatsby", "Harry Potter"],
                'non-fiction': ["Sapiens", "Atomic Habits", "Educated", "Becoming", "The 7 Habits"],
                'sci-fi': ["Dune", "Foundation", "Ender's Game", "The Hitchhiker's Guide", "Neuromancer"],
                'mystery': ["Gone Girl", "The Girl with the Dragon Tattoo", "Big Little Lies", "The Silent Patient"]
            }
        }
    
    def enhanced_web_search(self, query):
        """Enhanced web search with multiple approaches"""
        results = []
        
        try:
            # Try DuckDuckGo Instant Answer API
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
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
                    
        except Exception as e:
            print(f"Search API error: {e}")
        
        # Try alternative search approaches if no results
        if not results:
            try:
                # Try with more specific query
                specific_queries = {
                    'cars': 'automobile vehicle transportation',
                    'ai': 'artificial intelligence machine learning',
                    'programming': 'software development coding',
                    'python': 'python programming language'
                }
                
                for key, specific_query in specific_queries.items():
                    if key in query.lower():
                        url = f"https://api.duckduckgo.com/?q={specific_query}&format=json&no_html=1&skip_disambig=1"
                        response = requests.get(url, timeout=5)
                        data = response.json()
                        
                        if data.get('Abstract'):
                            results.append(f"Search result: {data['Abstract']}")
                            break
                            
            except Exception as e:
                print(f"Alternative search error: {e}")
        
        return "\n".join(results) if results else None
    
    def get_entertainment_recommendations(self, query):
        """Get entertainment recommendations from built-in database"""
        query_lower = query.lower()
        
        # Movie recommendations
        if any(word in query_lower for word in ['movie', 'film', 'cinema']):
            # Determine genre preference
            if any(genre in query_lower for genre in ['action', 'fight', 'adventure']):
                movies = self.entertainment_db['movies']['action']
                return f"🎬 **Great Action Movies:**\n• " + "\n• ".join(movies) + "\n\nThese are all highly-rated action films with great reviews!"
            
            elif any(genre in query_lower for genre in ['funny', 'comedy', 'laugh']):
                movies = self.entertainment_db['movies']['comedy']
                return f"😂 **Hilarious Comedy Movies:**\n• " + "\n• ".join(movies) + "\n\nThese comedies are guaranteed to make you laugh!"
            
            elif any(genre in query_lower for genre in ['drama', 'emotional', 'serious']):
                movies = self.entertainment_db['movies']['drama']
                return f"🎭 **Powerful Drama Movies:**\n• " + "\n• ".join(movies) + "\n\nThese dramas are critically acclaimed and emotionally powerful!"
            
            elif any(genre in query_lower for genre in ['sci-fi', 'science fiction', 'future']):
                movies = self.entertainment_db['movies']['sci-fi']
                return f"🚀 **Mind-Bending Sci-Fi Movies:**\n• " + "\n• ".join(movies) + "\n\nThese sci-fi films will blow your mind!"
            
            elif any(genre in query_lower for genre in ['horror', 'scary', 'frightening']):
                movies = self.entertainment_db['movies']['horror']
                return f"😱 **Scary Horror Movies:**\n• " + "\n• ".join(movies) + "\n\nThese horror films are genuinely terrifying!"
            
            elif any(genre in query_lower for genre in ['animated', 'cartoon', 'animation']):
                movies = self.entertainment_db['movies']['animated']
                return f"🎨 **Amazing Animated Movies:**\n• " + "\n• ".join(movies) + "\n\nThese animated films are masterpieces for all ages!"
            
            elif any(word in query_lower for word in ['recent', 'new', 'latest', '2023', '2024', '2025']):
                movies = self.entertainment_db['movies']['recent']
                return f"🆕 **Recent Great Movies:**\n• " + "\n• ".join(movies) + "\n\nThese are some of the best recent releases!"
            
            else:
                # General movie recommendations
                all_categories = []
                for category, movie_list in self.entertainment_db['movies'].items():
                    if category != 'recent':
                        all_categories.append(f"**{category.title()}:** {', '.join(movie_list[:3])}")
                
                return f"🎬 **Popular Movie Recommendations:**\n\n" + "\n\n".join(all_categories) + "\n\nWhat genre interests you most?"
        
        # Book recommendations
        elif any(word in query_lower for word in ['book', 'novel', 'read']):
            if any(genre in query_lower for genre in ['fiction', 'story', 'novel']):
                books = self.entertainment_db['books']['fiction']
                return f"📚 **Classic Fiction Books:**\n• " + "\n• ".join(books) + "\n\nThese are timeless literary classics!"
            
            elif any(genre in query_lower for genre in ['non-fiction', 'real', 'biography', 'self-help']):
                books = self.entertainment_db['books']['non-fiction']
                return f"📖 **Great Non-Fiction Books:**\n• " + "\n• ".join(books) + "\n\nThese books will expand your knowledge and change your perspective!"
            
            else:
                return f"📚 **Book Recommendations:**\n\n**Fiction:** {', '.join(self.entertainment_db['books']['fiction'][:3])}\n**Non-Fiction:** {', '.join(self.entertainment_db['books']['non-fiction'][:3])}\n**Sci-Fi:** {', '.join(self.entertainment_db['books']['sci-fi'][:3])}\n\nWhat type of books do you enjoy?"
        
        return None

    def get_knowledge_base_info(self, query):
        """Get information from built-in knowledge base"""
        query_lower = query.lower()
        
        # Check for matches in knowledge base
        for topic, info in self.knowledge_base.items():
            if topic in query_lower or any(word in query_lower for word in topic.split()):
                response = f"**{topic.title()}:**\n\n{info['info']}\n\n**Key Points:**\n"
                for i, detail in enumerate(info['details'], 1):
                    response += f"{i}. {detail}\n"
                return response
        
        return None
    
    def generate_smart_response(self, user_message, search_context="", kb_context=""):
        """Generate response using multiple information sources"""
        
        message_lower = user_message.lower()
        
        # Handle greetings
        if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm your AI assistant with access to web search and knowledge base. I can help you with information on many topics including cars, programming, AI, and more. What would you like to know?"
        
        # Handle questions about the assistant
        if any(phrase in message_lower for phrase in ['who are you', 'what are you', 'about you']):
            return "I'm an enhanced AI assistant that combines web search, built-in knowledge, and smart responses. I can provide information on a wide range of topics!"
        
        # If we have knowledge base information, prioritize it
        if kb_context:
            if search_context:
                return f"{kb_context}\n\n**Additional Web Information:**\n{search_context}\n\nWould you like to know anything specific about this topic?"
            else:
                return f"{kb_context}\n\nWould you like me to search for more current information about this topic?"
        
        # Handle search results
        if search_context:
            return f"Here's what I found:\n\n{search_context}\n\nWould you like me to search for more specific information about any aspect?"
        
        # Handle math questions
        if any(word in message_lower for word in ['calculate', 'math', '+', '-', '*', '/', 'equals', 'what is']) and any(char.isdigit() for char in user_message):
            try:
                import re
                # Extract mathematical expression
                math_pattern = r'[\d\s\+\-\*\/\(\)\.]+$'
                expression = user_message.replace('what is', '').replace('calculate', '').strip()
                if re.match(math_pattern, expression):
                    result = eval(expression)
                    return f"**Math Result:** {expression} = {result}"
            except:
                pass
            return "I can help with basic math. Try asking something like 'what is 15 + 25' or 'calculate 10 * 5'."
        
        # Handle specific topics that weren't found in search
        topic_responses = {
            'cars': "Cars are fascinating! They're motor vehicles designed for road transportation, typically with four wheels and powered by internal combustion engines or electric motors. Would you like to know about car history, types of cars, how engines work, or something specific?",
            'programming': "Programming is the art and science of creating software! It involves writing instructions for computers using programming languages like Python, JavaScript, or Java. Are you interested in learning programming, or do you have specific questions about coding?",
            'ai': "Artificial Intelligence is technology that enables machines to perform tasks requiring human-like intelligence. This includes learning, reasoning, and problem-solving. AI powers everything from smartphones to self-driving cars. What aspect of AI interests you most?",
            'python': "Python is an amazing programming language! It's known for being beginner-friendly yet powerful enough for complex applications. It's used in web development, data science, AI, and automation. Are you looking to learn Python or have specific questions about it?"
        }
        
        for topic, response in topic_responses.items():
            if topic in message_lower:
                return response
        
        # Default intelligent response with better search result handling
        if search_context:
            return f"Here's what I found about '{user_message}':\n\n{search_context}\n\nWould you like to know more about any specific aspect?"
        else:
            # Try to be helpful even without search results
            if any(word in message_lower for word in ['flower', 'plant', 'garden']):
                return "I'd be happy to help with gardening and flower questions! While I don't have specific flower information in my knowledge base, I can search for current information about flowers, gardening tips, or specific plant care. What specifically would you like to know about flowers?"
            elif any(word in message_lower for word in ['food', 'recipe', 'cooking']):
                return "I can help with food and cooking questions! Let me search for information about recipes, cooking techniques, or food recommendations. What specifically are you looking to cook or learn about?"
            elif any(word in message_lower for word in ['movie', 'film', 'book', 'music']):
                return "I can help with entertainment recommendations! While I don't have a built-in database of movies/books/music, I can search for current reviews, recommendations, and information. What genre or type are you interested in?"
            else:
                return f"That's an interesting question about '{user_message}'. I tried to search for information but didn't find specific results. Could you rephrase your question or be more specific? I'm great at finding information about most topics when given clear search terms!"
    
    def chat(self, user_message):
        """Main chat function with enhanced capabilities"""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        print("🧠 Thinking...")
        
        # First, check for entertainment recommendations
        entertainment_result = self.get_entertainment_recommendations(user_message)
        if entertainment_result:
            print("🎬 Found entertainment recommendations!")
            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": entertainment_result})
            
            # Keep history manageable
            if len(self.conversation_history) > 12:
                self.conversation_history = self.conversation_history[-8:]
            
            return entertainment_result
        
        # Then, check built-in knowledge base
        kb_context = self.get_knowledge_base_info(user_message)
        if kb_context:
            print("📚 Found information in knowledge base!")
        
        # Check if this needs a web search (expanded triggers)
        search_triggers = [
            'what is', 'who is', 'tell me about', 'explain', 'define', 'how to', 
            'information about', 'which', 'best', 'recommend', 'compare', 'where',
            'when', 'why', 'how much', 'how many', 'what are', 'find', 'search',
            'help me', 'tell me', 'show me'
        ]
        
        # Always search if it's a question or if no knowledge base match
        is_question = user_message.strip().endswith('?') or any(q_word in user_message.lower().split()[:2] for q_word in ['what', 'who', 'where', 'when', 'why', 'how', 'which'])
        needs_search = any(trigger in user_message.lower() for trigger in search_triggers) or is_question or not kb_context
        
        search_context = ""
        if needs_search:
            print("🔍 Searching web for additional information...")
            search_result = self.enhanced_web_search(user_message)
            if search_result:
                search_context = search_result
                print("✅ Found web information!")
            else:
                print("ℹ️ No additional web results found")
        
        # Generate response using all available information
        response = self.generate_smart_response(user_message, search_context, kb_context)
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.conversation_history) > 12:
            self.conversation_history = self.conversation_history[-8:]
        
        return response
    
    def add_to_knowledge_base(self, topic, info, details):
        """Add new information to knowledge base"""
        self.knowledge_base[topic.lower()] = {
            'info': info,
            'details': details if isinstance(details, list) else [details]
        }
        print(f"✅ Added {topic} to knowledge base!")
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🧹 Conversation history cleared!")

def main():
    print("🤖 Enhanced Free AI Assistant")
    print("=" * 35)
    print("Features:")
    print("✅ Built-in knowledge base")
    print("✅ Web search integration") 
    print("✅ Math calculations")
    print("✅ Smart conversation")
    print("=" * 35)
    print("Commands:")
    print("- 'quit' or 'exit': Exit")
    print("- 'clear': Clear history")
    print("- 'topics': Show knowledge base topics")
    print("=" * 35)
    
    chatbot = ImprovedFreeAIChatbot()
    
    print("✅ Ready! I have built-in knowledge about:")
    print("   🚗 Cars and transportation")
    print("   💻 Programming and Python")
    print("   🤖 Artificial Intelligence")
    print("   📊 Math and calculations")
    print()
    print("💡 Try asking:")
    print("   • 'Tell me about cars'")
    print("   • 'What is Python programming?'")
    print("   • 'Explain artificial intelligence'")
    print("   • 'Calculate 25 * 8'")
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
                
            elif user_input.lower() == 'topics':
                print("📚 Available knowledge base topics:")
                for topic in chatbot.knowledge_base.keys():
                    print(f"   • {topic.title()}")
                continue
            
            elif not user_input:
                continue
            
            # Get chatbot response
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
