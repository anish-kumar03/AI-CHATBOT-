import os
from datetime import datetime
from typing import Dict, List, Optional

import google.generativeai as genai
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

MAX_HISTORY_MESSAGES = 20
CONTEXT_WINDOW = 6

MODEL_OPTIONS: Dict[str, str] = {
    "gemini-1.5-flash": "Fastest responses",
    "gemini-1.5-pro": "Best quality and capabilities",
    "gemini-pro": "Standard model",
}


def get_secret_or_env(name: str) -> Optional[str]:
    value = st.secrets.get(name) if hasattr(st, "secrets") else None
    if value:
        return str(value).strip()
    env_value = os.getenv(name)
    return env_value.strip() if env_value else None


@st.cache_data(ttl=900, show_spinner=False)
def web_search(query: str) -> str:
    try:
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1,
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()

        results: List[str] = []
        if data.get("Abstract"):
            results.append(f"Search: {data['Abstract']}")
        if data.get("Answer"):
            results.append(f"Answer: {data['Answer']}")

        for topic in data.get("RelatedTopics", [])[:2]:
            if isinstance(topic, dict) and topic.get("Text"):
                text = topic["Text"]
                results.append(f"Related: {text[:220]}")

        return "\n".join(results)
    except requests.RequestException:
        return ""
    except ValueError:
        return ""


@st.cache_resource(show_spinner=False)
def get_model(model_name: str, api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def build_prompt(messages: List[Dict[str, str]], search_context: str) -> str:
    conversation_context = ""
    for msg in messages[-CONTEXT_WINDOW:]:
        conversation_context += f"{msg['role']}: {msg['content']}\n"

    now = datetime.utcnow().strftime("%Y-%m-%d")
    search_block = f"\nCurrent Information:\n{search_context}\n" if search_context else ""

    return (
        "You are a helpful, knowledgeable AI assistant. "
        "Provide accurate, concise, and conversational responses.\n"
        f"Current UTC date: {now}\n"
        f"{search_block}\n"
        f"{conversation_context}\n"
        "Please respond to the latest user message."
    )


def ensure_session_state() -> None:
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []


def generate_reply(user_message: str, model_name: str, enable_search: bool, api_key: str) -> str:
    history: List[Dict[str, str]] = st.session_state.conversation_history
    history.append({"role": "user", "content": user_message})

    search_context = ""
    if enable_search:
        with st.spinner("Searching for current information..."):
            search_context = web_search(user_message)

    prompt = build_prompt(history, search_context)

    try:
        model = get_model(model_name, api_key)
        with st.spinner("Generating response..."):
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=1500,
                    temperature=0.7,
                ),
            )

        reply = (response.text or "").strip()
        if not reply:
            reply = "Sorry, I could not generate a response. Please try again."

        history.append({"role": "assistant", "content": reply})
        if len(history) > MAX_HISTORY_MESSAGES:
            st.session_state.conversation_history = history[-12:]

        return reply
    except Exception as exc:
        error_text = str(exc).lower()
        if "quota" in error_text or "limit" in error_text:
            return "API quota exceeded. Please try again in a moment."
        if "api" in error_text or "key" in error_text or "permission" in error_text:
            return "API key error. Verify GEMINI_API_KEY in Streamlit secrets."
        return "Unexpected model error. Please retry your request."


def main() -> None:
    st.set_page_config(page_title="AI Chatbot", page_icon="AI", layout="wide")
    st.title("AI Chatbot")
    st.caption("Gemini-powered chat assistant")

    api_key = get_secret_or_env("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("GEMINI_API_KEY is not configured.")
        st.info("Set it in Streamlit secrets for deployment, or in a local .env file.")
        st.stop()

    ensure_session_state()

    with st.sidebar:
        st.header("Settings")
        selected_model = st.selectbox(
            "Gemini model",
            list(MODEL_OPTIONS.keys()),
            format_func=lambda model: f"{model} - {MODEL_OPTIONS[model]}",
            index=0,
        )
        enable_search = st.checkbox("Enable web search", value=False)
        if st.button("Clear conversation"):
            st.session_state.conversation_history = []
            st.rerun()

        st.markdown("---")
        st.write(f"Messages: {len(st.session_state.conversation_history)}")

    for message in st.session_state.conversation_history:
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.chat_message("user").write(user_input)
        with st.chat_message("assistant"):
            st.write(generate_reply(user_input, selected_model, enable_search, api_key))


if __name__ == "__main__":
    main()
