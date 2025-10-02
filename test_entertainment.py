#!/usr/bin/env python3

from enhanced_ai_chatbot import ImprovedFreeAIChatbot

def test_movie_recommendations():
    """Test movie recommendation functionality"""
    print("🧪 Testing Movie Recommendations...")
    print("=" * 50)
    
    chatbot = ImprovedFreeAIChatbot()
    
    test_queries = [
        "suggest me some good movies?",
        "recommend action movies",
        "what are good comedy films?",
        "suggest some books to read"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 40)
        
        response = chatbot.chat(query)
        print(f"Response preview: {response[:150]}...")
        
        if any(indicator in response for indicator in ["**", "•", "Great", "Popular", "Amazing"]):
            print("✅ SUCCESS: Got recommendations!")
        else:
            print("❌ FAILED: No proper recommendations")

if __name__ == "__main__":
    test_movie_recommendations()
