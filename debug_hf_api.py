import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_different_endpoints():
    """Test different Hugging Face API approaches"""
    
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"✅ Testing with API key: {api_key[:15]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    # Test 1: Check API status
    print("\n1️⃣ Testing API authentication...")
    try:
        response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)
        if response.status_code == 200:
            print("✅ Authentication working")
        else:
            print(f"❌ Auth failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Auth error: {e}")
    
    # Test 2: Try text generation with different models
    models_to_try = [
        "distilgpt2",
        "gpt2", 
        "microsoft/DialoGPT-small",
        "EleutherAI/gpt-neo-125M",
        "bigscience/bloom-560m"
    ]
    
    for model in models_to_try:
        print(f"\n2️⃣ Testing model: {model}")
        
        try:
            url = f"https://api-inference.huggingface.co/models/{model}"
            payload = {
                "inputs": "Hello, how are you?",
                "parameters": {"max_new_tokens": 10}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS! Model {model} is working")
                print(f"   Response: {response.json()}")
                break
            elif response.status_code == 503:
                print(f"   ⏳ Model loading...")
            elif response.status_code == 429:
                print(f"   ⏳ Rate limited")
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n3️⃣ Trying different API approach...")
    # Test 3: Try with pipeline API
    try:
        url = "https://api-inference.huggingface.co/pipeline/text-generation/gpt2"
        payload = {"inputs": "The weather today is"}
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"Pipeline API Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Pipeline API working!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Pipeline failed: {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ Pipeline error: {e}")

if __name__ == "__main__":
    test_different_endpoints()
