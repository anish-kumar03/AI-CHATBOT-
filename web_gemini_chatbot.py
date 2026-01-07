import streamlit as st
import os
import requests
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class StreamlitGeminiChatbot:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.gemini_api_key or self.gemini_api_key == 'your_gemini_api_key_here':
            st.error("❌ Please set your GEMINI_API_KEY in the .env file")
            st.info("Get one from: https://makersuite.google.com/app/apikey")
            return
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        
        # Available models
        self.models = {
            'gemini-1.5-flash': 'Fastest responses',
            'gemini-1.5-pro': 'Best quality and capabilities',
            'gemini-pro': 'Standard model'
        }
    
    def web_search(self, query):
        """Web search using DuckDuckGo"""
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            results = []
            
            if data.get('Abstract'):
                results.append(f"🔍 {data['Abstract']}")
            
            if data.get('Answer'):
                results.append(f"💡 {data['Answer']}")
            
            for topic in data.get('RelatedTopics', [])[:2]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append(f"📄 {topic['Text'][:120]}...")
            
            return "\n".join(results) if results else None
            
        except Exception as e:
            st.error(f"Search error: {e}")
            return None
    
    def chat(self, user_message, model_name, enable_search=False):
        """Chat using Gemini"""
        
        # Get conversation history from session state
        conversation_history = st.session_state.get('conversation_history', [])
        
        # Add user message
        conversation_history.append({"role": "user", "content": user_message})
        
        # Search for additional context if needed
        search_context = ""
        if enable_search:
            with st.spinner("🔍 Searching for current information..."):
                search_result = self.web_search(user_message)
                if search_result:
                    search_context = f"\n\nCurrent Information:\n{search_result}\n"
                    st.success("✅ Found additional context!")
        
        # Prepare conversation context
        conversation_context = ""
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            conversation_context += f"{msg['role']}: {msg['content']}\n"
        
        # Create prompt
        full_prompt = f"""You are a helpful, knowledgeable AI assistant. Provide accurate, informative, and conversational responses.

{search_context}

{conversation_context}

Please respond to the user's message in a helpful and engaging way."""
        
        try:
            # Generate response using Gemini
            model = genai.GenerativeModel(model_name)
            
            with st.spinner("🤖 Gemini is thinking..."):
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=1500,
                        temperature=0.7
                    )
                )
            
            if response.text:
                bot_response = response.text.strip()
                
                # Add to conversation history
                conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Keep history manageable
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-12:]
                
                # Update session state
                st.session_state.conversation_history = conversation_history
                
                return bot_response
            else:
                return "❌ Sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            
            if "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return "⏳ API quota exceeded. Please wait and try again."
            elif "api" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API key issue. Please check your GEMINI_API_KEY."
            else:
                return f"❌ Error: {str(e)[:100]}..."

def main():
    st.set_page_config(
        page_title="AI CHATBOT",
        page_icon="#",
        layout="wide"
    )
    
    st.title("🚀 AI CHATBOT - BUILD BY ARYA")
    st.markdown("*Powered by Google's fast and intelligent Gemini AI*")
    
    # Initialize chatbot
    chatbot = StreamlitGeminiChatbot()
    
    # Check API key
    if not chatbot.gemini_api_key or chatbot.gemini_api_key == 'your_gemini_api_key_here':
        st.stop()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model selection
        selected_model = st.selectbox(
            "Choose Gemini Model:",
            list(chatbot.models.keys()),
            format_func=lambda x: f"{x} - {chatbot.models[x]}",
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
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Tips")
        st.markdown("""
        - **Enable Search** for current information
        - **Try different models** for varied responses
        - **Ask follow-up questions** for deeper insights
        """)
    
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎬 Movie Suggestions"):
            st.session_state.example_query = "Suggest some good movies to watch this weekend"
    
    with col2:
        if st.button("💻 Programming Help"):
            st.session_state.example_query = "Explain Python functions with examples"
    
    with col3:
        if st.button("🌍 Current Events"):
            st.session_state.example_query = "What are the latest developments in AI technology?"
    
    with col4:
        if st.button("🧠 Creative Writing"):
            st.session_state.example_query = "Write a short story about a robot learning to paint"
    
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
    
    # Performance info
    with st.expander("ℹ️ About Gemini AI"):
        st.markdown("""
        **Why Gemini is better than Hugging Face free tier:**
        - ⚡ **Much faster response times**
        - 🧠 **More intelligent and accurate responses**
        - 🔄 **Better conversation flow and context understanding**
        - 📝 **Superior text generation quality**
        - 🚀 **More reliable API with higher limits**
        - 💰 **Generous free tier (15 requests per minute)**
        
        **Models:**
        - **gemini-1.5-flash**: Fastest responses, great for quick questions
        - **gemini-1.5-pro**: Best quality, perfect for complex tasks
        - **gemini-pro**: Standard model, good balance of speed and quality
        """)

if __name__ == "__main__":
    main()
