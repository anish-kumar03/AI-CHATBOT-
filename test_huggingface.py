import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

def test_huggingface_setup():
    """Test if Hugging Face API key is properly set up"""
    
    print("🧪 Testing Hugging Face Setup...")
    print("=" * 40)
    
    # Check if API key is set
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    if not api_key or api_key == 'your_actual_huggingface_token_here':
        print("❌ HUGGINGFACE_API_KEY not found in .env file")
        print("Please add your Hugging Face API key to the .env file")
        print("Get one from: https://huggingface.co/settings/tokens")
        return False
    
    print(f"✅ API Key found (starts with: {api_key[:10]}...)")
    
    # Test API connection with a simple model
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple text generation model
    test_url = "https://api-inference.huggingface.co/models/gpt2"
    test_payload = {
        "inputs": "Hello, this is a test",
        "parameters": {
            "max_new_tokens": 10
        }
    }
    
    try:
        print("🔄 Testing API connection...")
        response = requests.post(test_url, headers=headers, json=test_payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ API connection successful!")
            print("🎉 Your Hugging Face setup is working!")
            return True
        elif response.status_code == 503:
            print("⚠️  Model is loading (this is normal for first use)")
            print("✅ API key is valid - you can proceed!")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    test_huggingface_setup()
