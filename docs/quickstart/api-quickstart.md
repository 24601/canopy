# 🔌 API Quick Start Guide

Get started with Canopy's OpenAI-compatible API in minutes. Use Canopy with any OpenAI client library or tool!

## 🚀 Starting the API Server

```bash
# Start with default settings (port 8000)
python -m canopy --serve

# Custom port
python -m canopy --serve --port 3000

# With specific models available
python -m canopy --serve --models gpt-4o claude-3-sonnet gemini-pro
```

## 📡 API Endpoints

Base URL: `http://localhost:8000/v1`

### Available Endpoints

- `POST /v1/chat/completions` - Chat completions (OpenAI compatible)
- `GET /v1/models` - List available models
- `GET /health` - Health check
- `GET /v1/canopy/algorithms` - List available algorithms
- `POST /v1/canopy/analyze` - Analyze with specific algorithm

## 💻 Client Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

# Initialize client
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # Local server doesn't require auth
)

# Simple request
response = client.chat.completions.create(
    model="canopy-multi",
    messages=[
        {"role": "user", "content": "What is the meaning of life?"}
    ]
)

print(response.choices[0].message.content)
```

### Python (Streaming)

```python
# Streaming responses
stream = client.chat.completions.create(
    model="canopy-multi",
    messages=[
        {"role": "user", "content": "Write a short story about AI"}
    ],
    stream=True,
    extra_body={
        "agent_models": ["gpt-4o", "claude-3-haiku"],
        "stream_consensus": True  # Stream consensus process
    }
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')
```

### Python (Advanced Configuration)

```python
# Full configuration options
response = client.chat.completions.create(
    model="canopy-multi",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    extra_body={
        # Agent configuration
        "agent_models": ["gpt-4o", "claude-3-sonnet", "gemini-pro"],
        "algorithm": "treequest",  # or "massgen", "creative", "analytical"

        # Consensus settings
        "consensus_threshold": 0.8,  # 80% agreement required
        "max_debate_rounds": 5,      # Maximum rounds of discussion

        # Performance settings
        "max_duration": 300,         # Timeout in seconds
        "parallel_execution": True,   # Run agents in parallel

        # Output settings
        "include_reasoning": True,    # Include agent reasoning
        "include_consensus": True,    # Include consensus details
    }
)
```

### JavaScript/Node.js

```javascript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'not-needed',
});

async function askCanopy() {
  const response = await client.chat.completions.create({
    model: 'canopy-multi',
    messages: [
      { role: 'user', content: 'What are the pros and cons of nuclear energy?' }
    ],
    extra_body: {
      agent_models: ['gpt-4o', 'claude-3-sonnet', 'gemini-pro'],
      consensus_threshold: 0.75
    }
  });

  console.log(response.choices[0].message.content);
}

askCanopy();
```

### cURL

```bash
# Basic request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "canopy-multi",
    "messages": [
      {"role": "user", "content": "What is the best programming language?"}
    ],
    "agent_models": ["gpt-4o", "claude-3-haiku"]
  }'

# With all options
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "canopy-multi",
    "messages": [
      {"role": "user", "content": "Design a REST API for a todo app"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000,
    "agent_models": ["gpt-4o", "claude-3-sonnet", "gemini-pro"],
    "algorithm": "analytical",
    "consensus_threshold": 0.8,
    "include_reasoning": true
  }'
```

### HTTPie

```bash
# Install httpie: pip install httpie

# Simple request
http POST localhost:8000/v1/chat/completions \
  model=canopy-multi \
  messages:='[{"role": "user", "content": "Hello!"}]'

# With agent configuration
http POST localhost:8000/v1/chat/completions \
  model=canopy-multi \
  messages:='[{"role": "user", "content": "Compare SQL vs NoSQL"}]' \
  agent_models:='["gpt-4o", "claude-3-sonnet"]' \
  algorithm=analytical
```

## 🔧 API Configuration

### Model Selection

```python
# Use specific models
response = client.chat.completions.create(
    model="canopy-multi",
    messages=[{"role": "user", "content": "Hello"}],
    extra_body={
        "agent_models": ["gpt-4o", "claude-3-sonnet", "gemini-pro"]
    }
)

# Use model categories
response = client.chat.completions.create(
    model="canopy-multi",
    messages=[{"role": "user", "content": "Hello"}],
    extra_body={
        "agent_models": ["fast", "balanced", "powerful"],  # Predefined sets
    }
)
```

### Algorithm Selection

```python
# Available algorithms
algorithms = {
    "massgen": "Original parallel voting algorithm",
    "treequest": "Tree-based exploration for complex problems",
    "creative": "Optimized for creative tasks",
    "analytical": "Optimized for analysis and reasoning",
    "balanced": "General-purpose balanced approach"
}

# Use specific algorithm
response = client.chat.completions.create(
    model="canopy-multi",
    messages=[{"role": "user", "content": "Write a haiku"}],
    extra_body={
        "agent_models": ["gpt-4o", "claude-3-haiku"],
        "algorithm": "creative"
    }
)
```

## 📊 Response Format

### Standard Response

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "canopy-multi",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The consensus answer from all agents..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### Extended Response (with reasoning)

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "canopy-multi",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The consensus answer..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  },
  "canopy_metadata": {
    "algorithm": "treequest",
    "consensus_reached": true,
    "consensus_score": 0.85,
    "debate_rounds": 2,
    "agent_responses": [
      {
        "agent": "gpt-4o",
        "response": "Individual response...",
        "confidence": 0.9
      },
      {
        "agent": "claude-3-sonnet",
        "response": "Individual response...",
        "confidence": 0.8
      }
    ]
  }
}
```

## 🛠️ Special Endpoints

### List Available Models

```bash
curl http://localhost:8000/v1/models
```

Response:
```json
{
  "object": "list",
  "data": [
    {"id": "canopy-multi", "object": "model"},
    {"id": "gpt-4o", "object": "model"},
    {"id": "claude-3-sonnet", "object": "model"},
    {"id": "gemini-pro", "object": "model"}
  ]
}
```

### Get Available Algorithms

```bash
curl http://localhost:8000/v1/canopy/algorithms
```

Response:
```json
{
  "algorithms": [
    {
      "name": "massgen",
      "description": "Original parallel voting algorithm",
      "best_for": ["general", "quick_consensus"]
    },
    {
      "name": "treequest",
      "description": "Tree-based exploration algorithm",
      "best_for": ["complex_problems", "exploration"]
    }
  ]
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "available_models": 4,
  "uptime": 3600
}
```

## 🔐 Authentication (Optional)

By default, the local server doesn't require authentication. For production:

```bash
# Start with API key requirement
python -m canopy --serve --require-api-key YOUR_SECRET_KEY

# Client must then provide the key
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="YOUR_SECRET_KEY"
)
```

## 🌐 Integration Examples

### With LangChain

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",
    model="canopy-multi",
    model_kwargs={
        "extra_body": {
            "agent_models": ["gpt-4o", "claude-3-sonnet"],
            "algorithm": "analytical"
        }
    }
)

response = llm.invoke("What are the implications of AGI?")
```

### With Vercel AI SDK

```typescript
import { OpenAI } from 'ai/openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'not-needed',
});

const response = await client.chat.completions.create({
  model: 'canopy-multi',
  messages: [{ role: 'user', content: 'Hello!' }],
});
```

### With Gradio

```python
import gradio as gr
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

def chat_with_canopy(message):
    response = client.chat.completions.create(
        model="canopy-multi",
        messages=[{"role": "user", "content": message}],
        extra_body={"agent_models": ["gpt-4o", "claude-3-haiku"]}
    )
    return response.choices[0].message.content

interface = gr.Interface(
    fn=chat_with_canopy,
    inputs="text",
    outputs="text",
    title="Canopy Multi-Agent Chat"
)

interface.launch()
```

## 🚨 Error Handling

```python
try:
    response = client.chat.completions.create(
        model="canopy-multi",
        messages=[{"role": "user", "content": "Hello"}]
    )
except Exception as e:
    print(f"Error: {e}")
    # Error types:
    # - Connection errors: Server not running
    # - Configuration errors: Invalid models/parameters
    # - Timeout errors: Request took too long
    # - API errors: Invalid API usage
```

## 📈 Performance Tips

1. **Use faster models for quick responses**:
   ```python
   "agent_models": ["gpt-4o-mini", "claude-3-haiku", "gemini-flash"]
   ```

2. **Adjust consensus for speed vs quality**:
   ```python
   "consensus_threshold": 0.5,  # Lower = faster
   "max_debate_rounds": 2       # Fewer = faster
   ```

3. **Use streaming for better UX**:
   ```python
   stream=True
   ```

4. **Set appropriate timeouts**:
   ```python
   "max_duration": 60  # Don't wait forever
   ```

---

**Ready for more?** Check out the [full API documentation](../api-reference.md) or explore [advanced examples](../examples/)!
