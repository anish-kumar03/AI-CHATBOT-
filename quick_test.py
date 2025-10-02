import os
import requests
from dotenv import load_dotenv

load_dotenv()

def quick_test():
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ API Key: {api_key[:15]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with very simple prompt
    payload = {
        "inputs": "The capital of France is",
        "parameters": {
            "max_new_tokens": 5,
            "temperature": 0.1
        }
    }
    
    print("🔄 Testing GPT-2 model...")
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {result}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    quick_test()
