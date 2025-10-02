import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def test_huggingface_simple():
    """Simple test for Hugging Face API"""
    
    print("🧪 Testing Hugging Face API Connection...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    
    if not api_key or api_key == 'your_actual_huggingface_token_here':
        print("❌ HUGGINGFACE_API_KEY not found or not set properly")
        print("Please replace 'your_actual_huggingface_token_here' with your actual token")
        print("Get one from: https://huggingface.co/settings/tokens")
        return False
    
    print(f"✅ API Key found (starts with: {api_key[:10]}...)")
    
    # Test with a simple request
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    try:
        # Just test authentication with a simple GET request
        url = "https://huggingface.co/api/whoami-v2"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Authentication successful!")
            print(f"👤 Logged in as: {user_info.get('name', 'Unknown')}")
            print("🎉 Your Hugging Face setup is ready!")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print("Please check your API key")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    if test_huggingface_simple():
        print("\n🚀 You can now run: python huggingface_chatbot.py")
    else:
        print("\n❌ Please fix the API key issue before proceeding")
