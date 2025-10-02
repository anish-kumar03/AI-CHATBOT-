import streamlit as st
import openai
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="Factual AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitChatbot:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Optional Hugging Face fallback
        self.hf_key = os.getenv('HUGGINGFACE_API_KEY')
        self.hf_model = os.getenv('HUGGINGFACE_MODEL', 'mistralai/Mistral-7B-Instruct-v0.2')
    
    def get_response(self, question, use_web_search=False):
        messages = [
            {
                "role": "system",
                "content": f"""You are a helpful factual chatbot. Current date: 2025-08-08. 
                Provide accurate information and be honest about limitations. 
                For very recent events, suggest checking current news sources."""
            },
            {"role": "user", "content": question}
        ]
        
        web_context = None
        if use_web_search:
            web_context = self.simple_web_search(question)
            if web_context:
                context_text = f"Current web information: {web_context[:500]}..."
                messages.insert(1, {"role": "system", "content": context_text})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=600,
                temperature=0.2
            )
            return response.choices[0].message.content, web_context is not None
        except Exception as e:
            err = str(e)
            if "insufficient_quota" in err or "429" in err:
                return "Billing/quota error: your OpenAI API key has no available quota. Please add billing or use a different key.", False
            if "invalid_api_key" in err or "401" in err:
                return "Invalid API key. Please check OPENAI_API_KEY in your .env.", False
            return f"Error: {err}", False
    
    def simple_web_search(self, query):
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            return data.get('Abstract', '')
        except:
            return None

def main():
    st.title("🤖 Factual AI Chatbot")
    st.markdown("Ask me any factual question and I'll provide accurate information!")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = StreamlitChatbot()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        use_web_search = st.checkbox(
            "🌐 Enhanced web search", 
            value=False,
            help="Use web search for current information (slower but more current)"
        )
        
        st.header("📊 Statistics")
        st.metric("Questions Asked", len(st.session_state.messages) // 2)
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.header("💡 Tips")
        st.write("• Be specific in your questions")
        st.write("• For recent events, enable web search")
        st.write("• Ask follow-up questions for clarity")
        
        st.header("ℹ️ About")
        st.write("This chatbot uses OpenAI's GPT-3.5-turbo to answer factual questions.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("used_web_search"):
                st.caption("🌐 Enhanced with web search")
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response, used_web = st.session_state.chatbot.get_response(
                    prompt, use_web_search
                )
                st.markdown(response)
                if used_web:
                    st.caption("🌐 Enhanced with web search")
        
        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "used_web_search": used_web
        })

if __name__ == "__main__":
    main()