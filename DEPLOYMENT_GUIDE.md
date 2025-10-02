# Deployment Guide for Gemini-Powered Streamlit Chatbot
Version 1.0.0 | Last Updated: August 2025

## Table of Contents
- [1. Production Readiness](#1-production-readiness)
- [2. Deployment Platforms](#2-deployment-platforms)
- [3. Step-by-Step Deployment](#3-step-by-step-deployment)
- [4. Scaling Considerations](#4-scaling-considerations)

## 1. Production Readiness

### 1.1. Performance Optimizations

#### Caching Strategy
```python
# Add to web_gemini_chatbot.py
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_model_response(prompt, model_name):
    return chatbot.get_model_response(prompt, model_name)

@st.cache_resource
def initialize_chatbot():
    return GeminiChatbot()
```

#### Session Management
```python
# Add to web_gemini_chatbot.py
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_settings' not in st.session_state:
    st.session_state.user_settings = {
        'model': 'gemini-1.5-flash',
        'temperature': 0.7,
        'max_tokens': 1000
    }
```

### 1.2. Rate Limiting Implementation
```python
import time
from functools import wraps

def rate_limit(max_requests=60, window=60):
    def decorator(func):
        requests = []
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            requests[:] = [req for req in requests if req > now - window]
            if len(requests) >= max_requests:
                raise Exception("Rate limit exceeded. Please try again later.")
            requests.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Apply to chat method
@rate_limit(max_requests=60, window=60)
def chat(self, message):
    # Existing chat code
```

### 1.3. Error Handling
```python
def safe_chat_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again."
    return wrapper
```

### 1.4. Security Measures

#### API Key Protection
```python
# .gitignore
.env
*.pem
*.key
credentials/
```

#### Input Validation
```python
def validate_input(message):
    if len(message) > 4096:
        raise ValueError("Message too long")
    if not message.strip():
        raise ValueError("Empty message")
    # Add more validation as needed
    return message
```

### 1.5. Monitoring Setup
```python
import logging
from datetime import datetime

logging.basicConfig(
    filename='chatbot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def log_chat(user_message, bot_response, model_name):
    logging.info(f"""
    Time: {datetime.now()}
    User: {user_message[:100]}...
    Model: {model_name}
    Response: {bot_response[:100]}...
    """)
```

## 2. Deployment Platforms

### 2.1. Streamlit Community Cloud
- **Pros**:
  - Free tier available
  - Native Streamlit support
  - Easy deployment process
  - Automatic HTTPS
  - GitHub integration
- **Cons**:
  - Limited customization
  - No custom domain on free tier
  - Resource limitations
- **Best for**: Quick deployments, small to medium projects

### 2.2. Google Cloud Platform (GCP)
- **Pros**:
  - Highly scalable
  - Complete control
  - Load balancing
  - Auto-scaling
  - Custom domain support
- **Cons**:
  - More complex setup
  - Higher cost
  - Requires DevOps knowledge
- **Best for**: Enterprise deployments, high-traffic applications

### 2.3. Heroku
- **Pros**:
  - Easy deployment
  - Good free tier
  - Built-in CI/CD
  - Add-ons ecosystem
- **Cons**:
  - Can be expensive at scale
  - Limited free tier
  - Sleep on free tier
- **Best for**: Medium-sized projects, MVP deployments

## 3. Step-by-Step Deployment

### 3.1. Streamlit Community Cloud Deployment

1. **Prepare Your Repository**
```bash
# requirements.txt
streamlit==1.41.1
google-generativeai==0.3.0
python-dotenv==1.0.0
requests==2.32.3
```

2. **Create Config File**
```yaml
# .streamlit/config.toml
[server]
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false
```

3. **Deployment Steps**:
   1. Push code to GitHub
   2. Visit share.streamlit.io
   3. Connect your repository
   4. Add environment variables
   5. Deploy

### 3.2. Google Cloud Platform Deployment

1. **Dockerfile Creation**
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "web_gemini_chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Cloud Build Config**
```yaml
# cloudbuild.yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/chatbot', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/chatbot']
```

3. **Deployment Steps**:
   1. Install Google Cloud SDK
   2. Initialize project
   3. Enable required APIs
   4. Build and push container
   5. Deploy to Cloud Run

## 4. Scaling Considerations

### 4.1. Load Balancing
```yaml
# app.yaml (GCP)
runtime: custom
env: flex
automatic_scaling:
  target_cpu_utilization: 0.65
  min_num_instances: 2
  max_num_instances: 10
  cool_down_period_sec: 180
```

### 4.2. Database Integration
```python
# database.py
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(String, primary_key=True)
    user_message = Column(String)
    bot_response = Column(String)
    timestamp = Column(DateTime)
```

### 4.3. CDN Configuration
```yaml
# nginx.conf
http {
    upstream streamlit {
        server localhost:8501;
    }
    
    server {
        listen 80;
        server_name your-domain.com;
        
        location /static/ {
            proxy_cache STATIC;
            proxy_cache_use_stale error timeout http_500 http_502 http_503 http_504;
            proxy_cache_valid 200 60m;
            proxy_pass http://streamlit;
        }
    }
}
```

### 4.4. Auto-scaling Configuration
For GCP Cloud Run:
```bash
gcloud run deploy chatbot \
  --image gcr.io/PROJECT_ID/chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 2 \
  --max-instances 10 \
  --cpu 2 \
  --memory 4Gi
```

## Security Notes

1. **API Key Protection**:
   - NEVER commit .env files
   - Use secret management services
   - Rotate keys regularly

2. **Input Validation**:
   - Sanitize all user inputs
   - Implement rate limiting
   - Use CORS protection

3. **Monitoring**:
   - Set up error alerting
   - Monitor API quota usage
   - Track performance metrics

## Pre-deployment Checklist

- [ ] All sensitive data moved to environment variables
- [ ] Rate limiting implemented
- [ ] Error handling and logging in place
- [ ] Performance optimizations implemented
- [ ] Security measures tested
- [ ] Load testing completed
- [ ] Backup strategy defined
- [ ] Monitoring setup configured
- [ ] SSL/HTTPS enabled
- [ ] Documentation updated

## Post-deployment Monitoring

1. Set up monitoring for:
   - Response times
   - Error rates
   - API quota usage
   - Server resources
   - User metrics

2. Configure alerts for:
   - Error spikes
   - High latency
   - API quota approaching limits
   - Server resource constraints

Remember to test thoroughly in a staging environment before deploying to production.
