# AI Chatbot (Gemini + Streamlit)

Production-ready Streamlit chatbot optimized for Streamlit Community Cloud deployment.

## Features

- Gemini-powered conversational chat
- Optional web context from DuckDuckGo
- Streamlit session state for chat history
- Caching for model initialization and web search
- Safe environment handling with Streamlit secrets or local .env
- Linux-friendly pinned dependencies

## Project Structure

- app.py: Primary Streamlit application entry point
- streamlit_app.py: Streamlit Community Cloud compatible entry point
- requirements.txt: Fully pinned Python dependencies
- .streamlit/config.toml: Runtime and security-related Streamlit settings
- .env.example: Local development environment template

## Local Setup

1. Create and activate a virtual environment.
1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Create local environment file:

```bash
copy .env.example .env
```

1. Add your Gemini key in .env:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

1. Start app:

```bash
streamlit run app.py
```

## Streamlit Community Cloud Deployment

1. Push this repository to GitHub.
1. In Streamlit Community Cloud, create a new app from this repo.
1. Set Main file path to:

- streamlit_app.py (recommended)

1. Add secret in Streamlit App Settings -> Secrets:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

1. Deploy.

## Runtime Notes

- The app reads GEMINI_API_KEY from Streamlit secrets first, then falls back to environment variables.
- .env is for local development only and must never be committed.
- Cached web search results expire after 15 minutes.
- Model resource initialization is cached per selected model.

## Troubleshooting

- If you see API key errors, verify GEMINI_API_KEY exists in Streamlit secrets.
- If startup fails on cloud, confirm requirements.txt remains pinned and valid.
- If search context fails, chatbot still responds without web context.

## Security

- Do not commit .env or .streamlit/secrets.toml.
- Use Streamlit secrets for production credentials.

## License

MIT
