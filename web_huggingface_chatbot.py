import streamlit as st
import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class StreamlitHuggingFaceChatbot:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        
        # Free models you can use with Hugging Face
        self.model_options = {
            'Zephyr 7B (Recommended)': 'HuggingFaceH4/zephyr-7b-beta',
            'Llama 2 7B Chat': 'meta-llama/Llama-2-7b-chat-hf',
            'Mistral 7B': 'mistralai/Mistral-7B-Instruct-v0.1',
            'Falcon 7B': 'tiiuae/falcon-7b-instruct',
            'Code Llama 7B': 'codellama/CodeLlama-7b-Instruct-hf'
        }
        
        self.base_url = "https://api-inference.huggingface.co/models"
    
    def web_search(self, query, num_results=3):
        """Simple web search using DuckDuckGo Instant Answer API"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            search_results = []
            
            if data.get('Abstract'):
                search_results.append({
                    'title': data.get('AbstractSource', 'Web Search'),
                    'content': data['Abstract'],
                    'url': data.get('AbstractURL', '')
                })
            
            for topic in data.get('RelatedTopics', [])[:2]:
                if isinstance(topic, dict) and topic.get('Text'):
                    search_results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1],
                        'content': topic['Text'][:200] + '...',
                        'url': topic.get('FirstURL', '')
                    })
            
            return search_results if search_results else None
            
        except Exception as e:
            st.error(f"Web search error: {e}")
            return None
    
    def query_huggingface(self, model, payload):
        """Send request to Hugging Face API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{model}"
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"API request failed: {e}")
            return None
    
    def chat(self, user_message, model_key, use_search=False):
        """Main chat function"""
        if not self.api_key:
            return "❌ Please set your HUGGINGFACE_API_KEY in the .env file"
        
        context = ""
        if use_search:
            # Check if user wants web search
            search_keywords = ['search for', 'look up', 'find information about', 'what is', 'who is']
            needs_search = any(keyword in user_message.lower() for keyword in search_keywords) or use_search
            
            if needs_search:
                # Extract search query
                search_query = user_message.lower()
                for keyword in search_keywords:
                    if keyword in search_query:
                        search_query = search_query.split(keyword)[-1].strip()
                        break
                
                with st.spinner(f"🔍 Searching for: {search_query}"):
                    search_results = self.web_search(search_query)
                
                if search_results:
                    context = "\n\nWeb Search Results:\n"
                    for i, result in enumerate(search_results, 1):
                        context += f"{i}. {result['title']}: {result['content']}\n"
                    st.success("✅ Found relevant information")
                else:
                    st.warning("❌ No search results found")
        
        # Get conversation history from session state
        conversation_history = st.session_state.get('conversation_history', [])
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare the prompt for Hugging Face
        conversation = ""
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            conversation += f"{msg['role']}: {msg['content']}\n"
        
        if context:
            conversation += f"\nAdditional Context: {context}\n"
        
        # Get selected model
        model = self.model_options[model_key]
        
        # Different prompt formats for different models
        if 'zephyr' in model.lower():
            prompt = f"""<|system|>
You are a helpful, friendly AI assistant. Provide accurate, informative, and conversational responses.
</s>
<|user|>
{conversation}
</s>
<|assistant|>
"""
        elif 'llama' in model.lower():
            prompt = f"[INST] {conversation} [/INST]"
        else:
            prompt = f"Human: {conversation}\nAssistant:"
        
        # Query Hugging Face API
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        with st.spinner("🤖 Generating response..."):
            response = self.query_huggingface(model, payload)
        
        if response and isinstance(response, list) and len(response) > 0:
            bot_response = response[0].get('generated_text', '').strip()
            
            # Clean up the response
            if bot_response:
                # Remove any system tokens that might leak through
                bot_response = bot_response.replace('<|system|>', '').replace('<|user|>', '').replace('<|assistant|>', '').replace('</s>', '').strip()
                
                # Add to conversation history
                conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep conversation history manageable
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-10:]
                
                # Update session state
                st.session_state.conversation_history = conversation_history
                
                return bot_response
            else:
                return "I apologize, but I couldn't generate a proper response. Please try again."
        else:
            return "❌ Sorry, I'm having trouble connecting to the AI model. This might be due to high demand. Please try again in a moment."

def main():
    st.set_page_config(
        page_title="🤖 Hugging Face Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Hugging Face Chatbot")
    st.markdown("*Free alternative to OpenAI GPT models*")
    
    # Initialize chatbot
    chatbot = StreamlitHuggingFaceChatbot()
    
    # Check API key
    if not chatbot.api_key or chatbot.api_key == 'your_actual_huggingface_token_here':
        st.error("❌ Please set your HUGGINGFACE_API_KEY in the .env file")
        st.info("Get a free API key from: https://huggingface.co/settings/tokens")
        st.stop()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        selected_model = st.selectbox(
            "Choose AI Model:",
            list(chatbot.model_options.keys()),
            index=0
        )
        
        # Web search toggle
        enable_search = st.checkbox("🔍 Enable Web Search", value=False)
        
        # Clear conversation
        if st.button("🧹 Clear Conversation"):
            st.session_state.conversation_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Model Info")
        st.info(f"**Current Model:** {selected_model}")
        
        # Conversation stats
        history_len = len(st.session_state.get('conversation_history', []))
        st.info(f"**Messages:** {history_len}")
    
    # Initialize conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    # Display conversation history
    for i, message in enumerate(st.session_state.conversation_history):
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Get bot response
        with st.chat_message("assistant"):
            response = chatbot.chat(user_input, selected_model, enable_search)
            st.write(response)
    
    # Example prompts
    st.markdown("---")
    st.markdown("### 💡 Try these examples:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👋 Say Hello"):
            st.session_state.example_query = "Hello! How are you today?"
    
    with col2:
        if st.button("🧮 Solve Math"):
            st.session_state.example_query = "What is 15% of 240?"
    
    with col3:
        if st.button("💡 Get Ideas"):
            st.session_state.example_query = "Give me 3 creative ideas for a weekend project"
    
    # Handle example queries
    if 'example_query' in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
        
        # Display user message
        st.chat_message("user").write(query)
        
        # Get bot response
        with st.chat_message("assistant"):
            response = chatbot.chat(query, selected_model, enable_search)
            st.write(response)
        
        st.rerun()

if __name__ == "__main__":
    main()
