#!/usr/bin/env python3

from enhanced_ai_chatbot import ImprovedFreeAIChatbot

def test_cars_query():
    """Test the cars query specifically"""
    print("🧪 Testing 'Tell me about cars' query...")
    print("=" * 50)
    
    chatbot = ImprovedFreeAIChatbot()
    
    # Test the exact query you mentioned
    test_queries = [
        "Tell me about cars",
        "tell me about cars?", 
        "What are cars?",
        "Explain cars"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        print("-" * 30)
        
        response = chatbot.chat(query)
        print(f"Response: {response[:200]}...")
        
        if "Cars are motor vehicles" in response or "Cars:" in response:
            print("✅ SUCCESS: Found proper car information!")
        else:
            print("❌ FAILED: Did not find proper car information")

if __name__ == "__main__":
    test_cars_query()
