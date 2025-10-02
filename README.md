# 🤖 Multi-AI Chatbot System

A comprehensive chatbot project that integrates multiple AI providers (OpenAI GPT, Google Gemini, Hugging Face) with web search capabilities to provide intelligent, factual responses to real-world questions.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Architecture & Technology Stack](#architecture--technology-stack)
- [AI Models & LLM Details](#ai-models--llm-details)
- [How It Works Behind the Scenes](#how-it-works-behind-the-scenes)
- [Features & Capabilities](#features--capabilities)
- [Installation & Setup](#installation--setup)
- [Usage Examples](#usage-examples)
- [Technical Implementation Details](#technical-implementation-details)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Project Overview

This chatbot system is designed to provide **factual, intelligent answers** to real-world questions by leveraging multiple AI providers and web search integration. Unlike simple chatbots, this system:

- **Combines multiple AI models** for robust performance
- **Integrates web search** for current information
- **Provides fallback mechanisms** when primary services fail
- **Offers both CLI and web interfaces** for different use cases
- **Maintains conversation context** for natural interactions

**Primary Goal**: Create a reliable, intelligent assistant that can answer factual questions, provide recommendations, assist with coding, and engage in meaningful conversations while being resilient to API failures.

## 🏗️ Architecture & Technology Stack

### **Core Technologies**
- **Python 3.8+**: Main programming language
- **Streamlit**: Web interface framework
- **OpenAI GPT API**: Primary AI model (GPT-4, GPT-3.5-turbo)
- **Google Gemini API**: Fast, reliable AI alternative
- **Hugging Face API**: Open-source model fallback
- **DuckDuckGo API**: Web search integration
- **python-dotenv**: Environment variable management

### **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │  Web Interface  │    │  CLI Interface  │
│                 │    │   (Streamlit)   │    │    (Terminal)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │     Main Chatbot Core     │
                    │  (Request Processing)     │
                    └─────────────┬─────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
    ┌─────────▼─────────┐ ┌───────▼───────┐ ┌─────────▼─────────┐
    │    OpenAI API     │ │  Gemini API   │ │ Hugging Face API  │
    │   (Primary)       │ │  (Fast Alt)   │ │   (Fallback)      │
    └─────────┬─────────┘ └───────┬───────┘ └─────────┬─────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Web Search Engine      │
                    │   (DuckDuckGo API)        │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │   Response Generation     │
                    │   & Context Management    │
                    └───────────────────────────┘
```

### **Fallback Mechanism**
1. **Primary**: OpenAI GPT-4/3.5-turbo (high quality, paid)
2. **Secondary**: Google Gemini (fast, reliable, generous free tier)
3. **Tertiary**: Hugging Face models (free, slower)
4. **Quaternary**: Rule-based responses with web search

## 🧠 AI Models & LLM Details

### **Primary Models**

#### **OpenAI GPT-4 Turbo**
- **Model ID**: `gpt-4-turbo-preview`
- **Purpose**: Highest quality responses, complex reasoning
- **Parameters**:
  - Temperature: `0.7` (balanced creativity/accuracy)
  - Max tokens: `1000` (detailed responses)
  - Top-p: `1.0` (full vocabulary access)
- **Best for**: Complex analysis, creative writing, detailed explanations

#### **Google Gemini 1.5 Flash**
- **Model ID**: `gemini-1.5-flash`
- **Purpose**: Fast, reliable responses with good quality
- **Parameters**:
  - Temperature: `0.7` 
  - Max tokens: `1000`
  - Candidate count: `1`
- **Best for**: Quick questions, general conversation, real-time chat

#### **Hugging Face Models**
- **Primary**: `HuggingFaceH4/zephyr-7b-beta`
- **Fallbacks**: `meta-llama/Llama-2-7b-chat-hf`, `mistralai/Mistral-7B-Instruct-v0.1`
- **Parameters**:
  - Temperature: `0.7`
  - Max new tokens: `500`
  - Do sample: `true`
- **Best for**: Free usage, experimental features

### **Model Selection Logic**
- **Cost-aware**: Tries free/cheaper models first when appropriate
- **Quality-aware**: Uses premium models for complex queries
- **Speed-aware**: Prioritizes fast models for simple questions
- **Availability-aware**: Automatically falls back when services are down

## ⚙️ How It Works Behind the Scenes

### **Request Processing Flow**

1. **Input Analysis**
   ```python
   user_message = sanitize_input(raw_input)
   intent = analyze_intent(user_message)  # question, search, chat, code
   complexity = assess_complexity(user_message)  # simple, medium, complex
   ```

2. **Context Building**
   ```python
   conversation_history = get_recent_messages(limit=5)
   search_context = ""
   if needs_current_info(user_message):
       search_context = perform_web_search(user_message)
   ```

3. **Model Selection**
   ```python
   if complexity == "complex" and openai_available():
       model = select_openai_model()
   elif gemini_available():
       model = select_gemini_model()
   else:
       model = select_huggingface_model()
   ```

4. **Response Generation**
   ```python
   prompt = build_prompt(user_message, conversation_history, search_context)
   response = model.generate(prompt)
   response = post_process(response)
   ```

5. **Error Handling & Fallback**
   ```python
   try:
       return primary_model_response()
   except APIError:
       return fallback_model_response()
   except Exception:
       return rule_based_response()
   ```

### **Web Search Integration**

**Triggers**: Questions containing "what is", "who is", "current", "latest", "today", "recent"

**Process**:
1. Extract search query from user message
2. Call DuckDuckGo Instant Answer API
3. Parse and format results
4. Inject into AI model prompt as context
5. Generate enriched response

**Search Sources**:
- DuckDuckGo Instant Answers
- Wikipedia abstracts (via DuckDuckGo)
- Related topics and definitions

## ✨ Features & Capabilities

### **Core Functionality**
- 🤖 **Multi-AI Integration**: OpenAI, Gemini, Hugging Face
- 🔍 **Web Search Enhancement**: Real-time information retrieval
- 💭 **Conversation Memory**: Context-aware responses
- ⚡ **Fast Response Times**: 1-3 seconds typical response
- 🔄 **Automatic Fallbacks**: Seamless switching between AI providers
- 🎨 **Multiple Interfaces**: CLI, Web UI, and programmatic access

### **Question Types Supported**
- **Factual Questions**: "What is quantum computing?"
- **Current Events**: "What's happening in AI recently?"
- **How-to Guides**: "How do I learn Python?"
- **Comparisons**: "Compare iPhone vs Android"
- **Recommendations**: "Suggest good movies"
- **Code Help**: "Write a Python function to sort lists"
- **Creative Writing**: "Write a story about robots"
- **Math & Calculations**: "Calculate compound interest"
- **Analysis**: "Analyze pros and cons of remote work"

### **Web Interface Features**
- 📱 **Responsive Design**: Works on desktop and mobile
- ⚙️ **Model Selection**: Choose between AI providers
- 🔍 **Search Toggle**: Enable/disable web search
- 📊 **Conversation Stats**: Track usage and performance
- 🧹 **History Management**: Clear conversations
- 💾 **Session Persistence**: Maintains state across refreshes
- 🎨 **Syntax Highlighting**: Code responses with proper formatting

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package installer)
- Internet connection for API calls
- API keys (at least one of: OpenAI, Gemini, or Hugging Face)

### **Step 1: Clone the Repository**
```bash
git clone <repository-url>
cd multi-ai-chatbot
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: Environment Configuration**
Create a `.env` file in the project root:
```env
# Primary AI Provider (choose one or more)
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here

# Optional: News API (for enhanced search)
NEWS_API_KEY=your-news-api-key-here
```

### **Step 4: API Key Setup**

#### **OpenAI API Key** (Recommended for best quality)
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Add billing information (required for GPT-4)
4. Add key to `.env` file

#### **Google Gemini API Key** (Recommended for speed)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add key to `.env` file

#### **Hugging Face Token** (Free alternative)
1. Visit [Hugging Face Tokens](https://huggingface.co/settings/tokens)
2. Create a new token with "Read" permissions
3. Add token to `.env` file

### **Step 5: Run the Application**

**Web Interface (Recommended)**:
```bash
streamlit run web_gemini_chatbot.py
```

**Command Line Interface**:
```bash
python gemini_chatbot.py
```

**Test Setup**:
```bash
python test_gemini_setup.py
```

## 💡 Usage Examples

### **Basic Conversation**
```
You: Hello! How are you?
🤖 Gemini: Hello! I'm doing well, thank you for asking. I'm here and ready to help 
you with questions, tasks, or just have a conversation. How are you doing today? 
Is there anything specific you'd like to know or discuss?
```

### **Factual Questions**
```
You: What is machine learning?
🤖 Gemini: Machine learning is a subset of artificial intelligence (AI) that enables 
computer systems to automatically learn and improve from experience without being 
explicitly programmed...
[Detailed explanation continues]
```

### **Web Search Enhanced**
```
You: What are the latest developments in space exploration?
🔍 Searching for current information...
✅ Found additional context!
🤖 Gemini: Based on recent information, here are some of the latest developments 
in space exploration...
[Response includes current, up-to-date information]
```

### **Code Generation**
```
You: Write a Python function to calculate fibonacci numbers
🤖 Gemini: Here's a Python function to calculate Fibonacci numbers:

```python
def fibonacci(n):
    """
    Calculate the nth Fibonacci number using dynamic programming
    """
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Example usage
print(fibonacci(10))  # Output: 55
```

### **Web Interface Usage**
1. Open browser to `http://localhost:8501`
2. Select AI model from sidebar
3. Toggle web search if needed
4. Type question in chat input
5. View response with formatting
6. Continue conversation with context

## 🔧 Technical Implementation Details

### **Project Structure**
```
multi-ai-chatbot/
├── .env                          # Environment variables
├── requirements.txt              # Python dependencies
├── README.md                     # This documentation
│
├── Core Chatbot Files:
├── gemini_chatbot.py            # Gemini CLI chatbot (recommended)
├── web_gemini_chatbot.py        # Gemini web interface (recommended)
├── enhanced_chatbot.py          # OpenAI-based chatbot
├── web_chatbot.py              # OpenAI web interface
├── huggingface_chatbot.py      # Hugging Face chatbot
├── enhanced_ai_chatbot.py      # Multi-source chatbot
│
├── Testing & Utilities:
├── test_gemini_setup.py        # Gemini API testing
├── test_hf_simple.py           # Hugging Face testing
├── debug_hf_api.py             # API debugging tools
│
├── Legacy/Experimental:
├── basic_chatbot.py            # Simple implementation
├── advanced_chatbot.py         # Advanced features
├── free_ai_chatbot.py          # No-API version
└── hub_chatbot.py             # Alternative HF implementation
```

### **Key Classes and Methods**

#### **GeminiChatbot Class**
```python
class GeminiChatbot:
    def __init__(self):
        # Initialize Gemini API and configuration
        
    def chat(self, user_message, include_search=False):
        # Main conversation method
        
    def web_search(self, query):
        # Perform web search using DuckDuckGo
        
    def switch_model(self, model_name):
        # Change between Gemini models
```

#### **Enhanced Chatbot Features**
- **Conversation History**: Maintains context across messages
- **Smart Search**: Determines when web search is needed
- **Error Recovery**: Graceful handling of API failures
- **Response Formatting**: Clean, readable output

### **API Integration Patterns**

#### **OpenAI Integration**
```python
client = openai.OpenAI(api_key=api_key)
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=conversation_history,
    temperature=0.7,
    max_tokens=1000
)
```

#### **Gemini Integration**
```python
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(
    prompt,
    generation_config=genai.types.GenerationConfig(
        max_output_tokens=1000,
        temperature=0.7
    )
)
```

#### **Hugging Face Integration**
```python
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.post(
    f"https://api-inference.huggingface.co/models/{model}",
    headers=headers,
    json={"inputs": prompt, "parameters": params}
)
```

### **Error Handling Strategies**

1. **API Rate Limiting**
   ```python
   except RateLimitError:
       time.sleep(exponential_backoff)
       return fallback_response()
   ```

2. **Quota Exceeded**
   ```python
   except QuotaExceededError:
       return switch_to_alternative_provider()
   ```

3. **Network Issues**
   ```python
   except ConnectionError:
       return cached_response_or_offline_mode()
   ```

4. **Invalid API Keys**
   ```python
   except AuthenticationError:
       return "Please check your API configuration"
   ```

## ⚙️ Configuration Options

### **Environment Variables**

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Optional* | OpenAI API access key | None |
| `GEMINI_API_KEY` | Optional* | Google Gemini API key | None |
| `HUGGINGFACE_API_KEY` | Optional* | Hugging Face access token | None |
| `NEWS_API_KEY` | Optional | NewsAPI key for enhanced search | None |

*At least one AI provider API key is required

### **Model Configuration**

#### **Gemini Models**
```python
models = {
    'gemini-1.5-flash': 'Fastest responses',
    'gemini-1.5-pro': 'Best quality and capabilities', 
    'gemini-pro': 'Standard model'
}
```

#### **OpenAI Models**
```python
models = {
    'gpt-4-turbo-preview': 'Highest quality, slower',
    'gpt-3.5-turbo': 'Fast, good quality',
    'gpt-4': 'Best reasoning, expensive'
}
```

### **Response Parameters**
```python
# Customize in the respective chatbot files
TEMPERATURE = 0.7        # Creativity level (0.0-2.0)
MAX_TOKENS = 1000       # Response length limit
TOP_P = 1.0            # Vocabulary diversity
FREQUENCY_PENALTY = 0   # Repetition reduction
```

### **Web Search Settings**
```python
SEARCH_TRIGGERS = [
    'what is', 'who is', 'current', 'latest', 
    'today', 'recent', 'now'
]
MAX_SEARCH_RESULTS = 3
SEARCH_TIMEOUT = 5      # seconds
```

## 🔧 Troubleshooting

### **Common Issues**

#### **API Key Problems**
**Error**: `Invalid API key` or `Authentication failed`

**Solution**:
1. Check `.env` file exists and has correct keys
2. Verify API keys are active and have sufficient credits
3. Test with setup scripts: `python test_gemini_setup.py`

#### **Quota/Rate Limit Errors**
**Error**: `Rate limit exceeded` or `Quota exceeded`

**Solutions**:
- **OpenAI**: Check billing and usage at [OpenAI Usage](https://platform.openai.com/usage)
- **Gemini**: Wait for rate limit reset (usually 1 minute)
- **Switch models**: Use alternative AI provider
- **Reduce usage**: Implement request delays

#### **Slow Response Times**
**Possible Causes**:
- Using slower models (Hugging Face)
- Web search adding latency
- Network connectivity issues

**Solutions**:
1. Switch to Gemini (`gemini-1.5-flash`) for speed
2. Disable web search for simple questions
3. Check internet connection
4. Use local fallback responses

#### **Installation Issues**
**Error**: Package installation failures

**Solutions**:
```bash
# Update pip
python -m pip install --upgrade pip

# Install with specific versions
pip install -r requirements.txt --force-reinstall

# For M1 Macs (Apple Silicon)
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

#### **Streamlit Issues**
**Error**: `streamlit: command not found`

**Solutions**:
```bash
# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit

# Run with Python module
python -m streamlit run web_gemini_chatbot.py
```

### **Performance Optimization**

#### **Speed Improvements**
1. **Use Gemini Flash**: Fastest model available
2. **Disable search**: For simple questions
3. **Reduce history**: Limit conversation context
4. **Cache responses**: Store common answers

#### **Quality Improvements**
1. **Use GPT-4**: Best reasoning and accuracy
2. **Enable search**: For factual questions
3. **Longer context**: Include more conversation history
4. **Higher temperature**: For creative tasks

#### **Cost Optimization**
1. **Start with free models**: Gemini → Hugging Face
2. **Use GPT-3.5**: Instead of GPT-4 for simple tasks
3. **Limit tokens**: Reduce max_tokens parameter
4. **Smart routing**: Complex queries to premium models only

### **Debugging Tips**

#### **Enable Debug Mode**
Add to your `.env`:
```env
DEBUG=True
LOG_LEVEL=INFO
```

#### **Check API Status**
```python
# Test individual APIs
python test_gemini_setup.py
python test_hf_simple.py
python debug_hf_api.py
```

#### **Monitor Usage**
- **OpenAI**: [Usage Dashboard](https://platform.openai.com/usage)
- **Gemini**: [AI Studio](https://makersuite.google.com/)
- **Hugging Face**: Check rate limits in API responses

### **Getting Help**

1. **Check logs**: Look for error messages in terminal
2. **Test components**: Use individual test scripts
3. **Verify setup**: Run setup verification scripts
4. **Check documentation**: API provider documentation
5. **Community**: Stack Overflow, Reddit r/MachineLearning

## 📁 File Structure

### **Recommended Files for Production**
- `gemini_chatbot.py` - Primary CLI chatbot
- `web_gemini_chatbot.py` - Primary web interface
- `test_gemini_setup.py` - Setup verification
- `.env` - Configuration
- `requirements.txt` - Dependencies

### **Alternative Implementations**
- `enhanced_chatbot.py` - OpenAI-based version
- `enhanced_ai_chatbot.py` - Multi-provider with knowledge base
- `huggingface_chatbot.py` - Open-source models only
- `free_ai_chatbot.py` - No API keys required

### **Testing & Development**
- `test_*.py` - Various testing utilities
- `debug_*.py` - Debugging and API testing tools

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Add tests
6. Submit a pull request

### **Areas for Contribution**
- **New AI Providers**: Integrate Claude, Cohere, etc.
- **Enhanced Search**: Better web search integration
- **UI Improvements**: Better Streamlit interface
- **Performance**: Caching, optimization
- **Features**: Voice input, image generation
- **Documentation**: Examples, tutorials
- **Testing**: More comprehensive test coverage

### **Code Standards**
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write tests for new features
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Google** for Gemini AI
- **Hugging Face** for open-source models and hosting
- **Streamlit** for the web framework
- **DuckDuckGo** for search API
- **Python Community** for excellent libraries

## 📊 Project Status

- ✅ **Core functionality**: Complete
- ✅ **Multi-AI integration**: Complete  
- ✅ **Web interface**: Complete
- ✅ **Documentation**: Complete
- 🔄 **Voice interface**: In development
- 🔄 **Mobile app**: Planned
- 🔄 **Enterprise features**: Planned

---

**Built with ❤️ for the AI community**

*Last updated: August 2025*
