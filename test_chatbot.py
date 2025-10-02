import os
from dotenv import load_dotenv
import openai

load_dotenv()

def test_api_key():
    """Test if your OpenAI API key works"""
    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello!"}],
            max_tokens=50
        )
        
        print("✅ API key works!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ API key issue: {e}")
        return False

if __name__ == "__main__":
    test_api_key()