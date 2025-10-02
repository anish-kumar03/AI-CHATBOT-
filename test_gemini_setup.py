import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_gemini_setup():
    """Test Gemini API setup and functionality"""
    
    print("🧪 Testing Gemini API Setup...")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not found in .env file")
        print("\n📋 Setup Instructions:")
        print("1. Go to: https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Copy the key")
        print("4. Replace 'your_gemini_api_key_here' in your .env file")
        return False
    
    print(f"✅ API Key found (starts with: {api_key[:20]}...)")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ Gemini configured successfully")
        
        # Test different models
        models_to_test = [
            'gemini-1.5-flash',
            'gemini-1.5-pro', 
            'gemini-pro'
        ]
        
        working_models = []
        
        for model_name in models_to_test:
            try:
                print(f"\n🔄 Testing {model_name}...")
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    "Hello! Please respond with 'Gemini API is working perfectly!' and tell me your model name.",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=100,
                        temperature=0.1
                    )
                )
                
                if response.text:
                    print(f"✅ {model_name} working!")
                    print(f"   Response: {response.text[:80]}...")
                    working_models.append(model_name)
                else:
                    print(f"❌ {model_name} returned empty response")
                    
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)[:60]}...")
        
        if working_models:
            print(f"\n🎉 Success! {len(working_models)} Gemini models are working:")
            for model in working_models:
                print(f"   ✅ {model}")
            
            print(f"\n🚀 Recommended model: {working_models[0]} (fastest)")
            print("\n▶️  You can now run:")
            print("   python gemini_chatbot.py")
            print("   streamlit run web_gemini_chatbot.py")
            return True
        else:
            print("\n❌ No models are working. Please check your API key.")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Setup failed: {error_msg}")
        
        if "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print("\n💡 This looks like an API key issue:")
            print("1. Make sure you copied the full API key")
            print("2. Check that the API key is active")
            print("3. Ensure you have Gemini API access enabled")
        elif "quota" in error_msg.lower():
            print("\n💡 Quota exceeded - try again in a few minutes")
        
        return False

if __name__ == "__main__":
    if test_gemini_setup():
        print("\n🎯 Setup Complete! Your Gemini chatbot is ready!")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
