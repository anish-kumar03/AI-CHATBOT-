import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st
from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from dotenv import load_dotenv

load_dotenv(override=False)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 20
CONTEXT_WINDOW = 6

MODEL_OPTIONS: Dict[str, str] = {
    "gemini-flash-latest": "Recommended general model",
    "gemini-flash-lite-latest": "Faster and lower-cost model",
    "gemini-pro-latest": "Higher quality responses",
}

MODEL_CANDIDATES: List[str] = list(MODEL_OPTIONS.keys())


def get_secret_or_env(name: str) -> Optional[str]:
    if hasattr(st, "secrets") and name in st.secrets:
        value = str(st.secrets[name]).strip()
        if value:
            return value

    env_value = os.getenv(name)
    return env_value.strip() if env_value else None


def get_secret_or_env_with_source(name: str) -> Tuple[Optional[str], str]:
    if hasattr(st, "secrets") and name in st.secrets:
        value = str(st.secrets[name]).strip()
        if value:
            return value, "streamlit_secrets"

    env_value = os.getenv(name)
    if env_value and env_value.strip():
        return env_value.strip(), "environment"

    return None, "missing"


def is_debug_mode() -> bool:
    debug_value = get_secret_or_env("APP_DEBUG") or "false"
    return debug_value.lower() in {"1", "true", "yes", "on"}


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
def get_client(api_key: str) -> genai.Client:
    # Passing api_key directly avoids ambiguity with unrelated environment variables.
    return genai.Client(api_key=api_key)


@st.cache_data(ttl=3600, show_spinner=False)
def get_supported_models(api_key: str) -> List[str]:
    try:
        client = get_client(api_key)
        models = client.models.list()
        names: List[str] = []
        for model in models:
            name = getattr(model, "name", "") or ""
            if name.startswith("models/"):
                names.append(name.replace("models/", "", 1))
        return sorted(set(names))
    except Exception:
        return []


def resolve_model_name(requested_model: str, supported_models: List[str]) -> str:
    if requested_model in supported_models:
        return requested_model

    for candidate in MODEL_CANDIDATES:
        if candidate in supported_models:
            return candidate

    return requested_model


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


def handle_gemini_exception(exc: Exception) -> Tuple[str, str]:
    error_text = str(exc)
    lowered = error_text.lower()

    if "api key not valid" in lowered or "permission_denied" in lowered or "unauthenticated" in lowered:
        return (
            "Authentication failed with Gemini. Please verify the configured API key.",
            error_text,
        )

    if "quota" in lowered or "rate" in lowered or "429" in lowered or "resource_exhausted" in lowered:
        return (
            "Gemini API quota or rate limit reached. Please try again shortly.",
            error_text,
        )

    if "not found" in lowered and "model" in lowered:
        return (
            "Selected Gemini model is unavailable for this API key/project. Choose another model.",
            error_text,
        )

    if "deadline" in lowered or "timeout" in lowered or "unavailable" in lowered:
        return (
            "Gemini service is temporarily unavailable. Please retry in a moment.",
            error_text,
        )

    return (
        "Gemini request failed due to an unexpected error. Please try again.",
        error_text,
    )


def _is_model_unavailable_error(exc: Exception) -> bool:
    lowered = str(exc).lower()
    return (
        "not_found" in lowered
        or "not found" in lowered
        or "no longer available" in lowered
        or "currently experiencing high demand" in lowered
        or "temporarily unavailable" in lowered
        or "service unavailable" in lowered
        or ("model" in lowered and "unsupported" in lowered)
    )


def generate_with_fallback(
    client: genai.Client,
    model_name: str,
    prompt: str,
    supported_models: List[str],
):
    fallback_order = [
        model_name,
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-pro-latest",
    ]

    # Add any account-visible flash/pro models as additional fallbacks.
    dynamic_models = [
        model
        for model in supported_models
        if "flash" in model.lower() or "pro" in model.lower()
    ]

    tried: List[str] = []
    for candidate in fallback_order + dynamic_models:
        if candidate in tried:
            continue
        tried.append(candidate)

        try:
            return client.models.generate_content(
                model=candidate,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1500,
                ),
            )
        except (genai_errors.ClientError, genai_errors.ServerError) as exc:
            if _is_model_unavailable_error(exc):
                LOGGER.warning("Model %s unavailable, trying fallback", candidate)
                continue
            raise

    raise RuntimeError(
        "No available Gemini text model could process this request with the current project key."
    )


def generate_reply(
    user_message: str,
    model_name: str,
    enable_search: bool,
    api_key: str,
    supported_models: List[str],
) -> str:
    history: List[Dict[str, str]] = st.session_state.conversation_history
    history.append({"role": "user", "content": user_message})

    search_context = ""
    if enable_search:
        with st.spinner("Searching for current information..."):
            search_context = web_search(user_message)

    prompt = build_prompt(history, search_context)

    try:
        client = get_client(api_key)
        with st.spinner("Generating response..."):
            response = generate_with_fallback(client, model_name, prompt, supported_models)

        reply = (response.text or "").strip()
        if not reply:
            reply = "Sorry, I could not generate a response. Please try again."

        history.append({"role": "assistant", "content": reply})
        if len(history) > MAX_HISTORY_MESSAGES:
            st.session_state.conversation_history = history[-12:]

        return reply
    except (genai_errors.ClientError, genai_errors.ServerError, Exception) as exc:
        user_error, raw_error = handle_gemini_exception(exc)
        LOGGER.exception("Gemini request failed: %s", raw_error)
        if is_debug_mode():
            st.error(f"Gemini debug error: {raw_error}")
        return user_error


def main() -> None:
    st.set_page_config(page_title="AI Chatbot", page_icon="AI", layout="wide")
    st.title("AI Chatbot")
    st.caption("Gemini-powered chat assistant")

    api_key, key_source = get_secret_or_env_with_source("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        st.error("GEMINI_API_KEY is not configured.")
        st.info("Set it in Streamlit secrets for deployment, or in a local .env file.")
        st.stop()

    ensure_session_state()

    supported_models = get_supported_models(api_key)
    available_models = [m for m in MODEL_CANDIDATES if m in supported_models] if supported_models else MODEL_CANDIDATES
    if supported_models and not available_models:
        st.warning("No preferred Gemini models found for this key. Falling back to entered model name.")
        available_models = ["gemini-flash-latest"]

    with st.sidebar:
        st.header("Settings")
        selected_model = st.selectbox(
            "Gemini model",
            available_models,
            format_func=lambda model: f"{model} - {MODEL_OPTIONS[model]}",
            index=0,
        )
        enable_search = st.checkbox("Enable web search", value=False)
        if st.button("Clear conversation"):
            st.session_state.conversation_history = []
            st.rerun()

        st.markdown("---")
        st.write(f"Messages: {len(st.session_state.conversation_history)}")
        if is_debug_mode():
            st.caption(f"Key source: {key_source}")

    for message in st.session_state.conversation_history:
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("Type your message...")
    if user_input:
        st.chat_message("user").write(user_input)
        with st.chat_message("assistant"):
            effective_model = resolve_model_name(selected_model, supported_models)
            st.write(
                generate_reply(
                    user_input,
                    effective_model,
                    enable_search,
                    api_key,
                    supported_models,
                )
            )


if __name__ == "__main__":
    main()
