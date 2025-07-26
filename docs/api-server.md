# Canopy API Server

Canopy provides an OpenAI-compatible API server with additional A2A protocol support, allowing you to use the multi-agent consensus system through standard OpenAI client libraries and A2A-compatible tools.

## Features

- **OpenAI API Compatibility**: Drop-in replacement for OpenAI's Chat and Completions endpoints
- **Multi-Agent Support**: Leverage multiple AI models for consensus-based responses
- **Dynamic Configuration**: Configure agents, algorithms, and parameters per request
- **Streaming Support**: Real-time streaming responses for both chat and completions
- **Algorithm Selection**: Choose between MassGen and TreeQuest algorithms
- **Full Customization**: Override consensus thresholds, debate rounds, and more
- **A2A Protocol Support**: Standard agent-to-agent communication protocol

## Starting the Server

### Command Line

```bash
# Start with default settings (port 8000)
python cli.py --serve

# Custom port and host
python cli.py --serve --port 8080 --host localhost

# With a default configuration
python cli.py --serve --config examples/production.yaml
```

### Python

```python
import uvicorn
from massgen.api_server import app

uvicorn.run(app, host="0.0.0.0", port=8000)
```

## API Endpoints

### Chat Completions

`POST /v1/chat/completions`

Create a chat completion using the MassGen consensus system.

#### Request

```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "temperature": 0.7,
  "stream": false,
  
  // MassGen-specific extensions
  "agent_models": ["gpt-4", "claude-3-opus", "gemini-pro"],
  "algorithm": "massgen",
  "consensus_threshold": 0.66,
  "max_debate_rounds": 3
}
```

#### Response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The capital of France is Paris."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 7,
    "total_tokens": 20
  },
  "massgen_metadata": {
    "consensus_reached": true,
    "representative_agent": "agent_1",
    "debate_rounds": 1,
    "total_agents": 3,
    "algorithm": "massgen",
    "duration": 2.34
  }
}
```

### Text Completions

`POST /v1/completions`

Create a text completion using the MassGen consensus system.

#### Request

```json
{
  "model": "gpt-4",
  "prompt": "The capital of France is",
  "max_tokens": 10,
  "temperature": 0.5,
  "echo": false,
  
  // MassGen-specific extensions
  "agent_models": ["gpt-4", "claude-3"],
  "algorithm": "treequest"
}
```

#### Response

```json
{
  "id": "cmpl-xyz789",
  "object": "text_completion",
  "created": 1677858242,
  "model": "gpt-4",
  "choices": [
    {
      "text": " Paris, known for the Eiffel Tower.",
      "index": 0,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 6,
    "completion_tokens": 8,
    "total_tokens": 14
  },
  "massgen_metadata": {
    "consensus_reached": true,
    "representative_agent": "agent_0",
    "debate_rounds": 0,
    "total_agents": 2,
    "algorithm": "treequest",
    "duration": 1.89
  }
}
```

### List Models

`GET /v1/models`

List available model configurations.

#### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "massgen-gpt4",
      "object": "model",
      "created": 1686935002,
      "owned_by": "massgen"
    },
    {
      "id": "massgen-claude3",
      "object": "model",
      "created": 1686935002,
      "owned_by": "massgen"
    },
    {
      "id": "massgen-multi",
      "object": "model",
      "created": 1686935002,
      "owned_by": "massgen"
    }
  ]
}
```

### Health Check

`GET /health`

Check if the API server is running.

#### Response

```json
{
  "status": "healthy",
  "service": "massgen-api",
  "version": "1.0.0"
}
```

## Using with OpenAI Client Libraries

### Python

```python
from openai import OpenAI

# Point to your MassGen server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # MassGen uses your configured API keys
)

# Standard chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ]
)

# With multiple agents
response = client.chat.completions.create(
    model="massgen-multi",
    messages=[
        {"role": "user", "content": "What are the implications of AGI?"}
    ],
    extra_body={
        "agent_models": ["gpt-4", "claude-3-opus", "gemini-pro"],
        "consensus_threshold": 0.75,
        "algorithm": "massgen"
    }
)

# Streaming
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
```

### JavaScript/TypeScript

```javascript
import OpenAI from 'openai';

const openai = new OpenAI({
  baseURL: 'http://localhost:8000/v1',
  apiKey: 'not-needed',
});

// Chat completion
const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'What is recursion?' }],
});

// With MassGen features
const multiAgentResponse = await openai.chat.completions.create({
  model: 'massgen-multi',
  messages: [{ role: 'user', content: 'Explain consciousness' }],
  agent_models: ['gpt-4', 'claude-3', 'gemini-pro'],
  consensus_threshold: 0.8,
});
```

### cURL

```bash
# Basic chat completion
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# With multiple agents
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "massgen-multi",
    "messages": [{"role": "user", "content": "What is consciousness?"}],
    "agent_models": ["gpt-4", "claude-3-opus"],
    "consensus_threshold": 0.75
  }'
```

## Configuration Options

### Request Parameters

All standard OpenAI parameters are supported, plus:

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `agent_models` | `string[]` | List of models for agents | Uses config file |
| `algorithm` | `string` | Algorithm to use (`massgen` or `treequest`) | `massgen` |
| `consensus_threshold` | `float` | Consensus threshold (0.0-1.0) | `0.51` |
| `max_debate_rounds` | `int` | Maximum debate rounds | `3` |
| `config_path` | `string` | Path to config file | `None` |

### Using Configuration Files

You can reference existing configuration files in your requests:

```json
{
  "model": "massgen-multi",
  "messages": [{"role": "user", "content": "Question"}],
  "config_path": "/path/to/config.yaml"
}
```

## Advanced Usage

### Dynamic Agent Selection

Select different agents based on the task:

```python
# For creative tasks
creative_response = client.chat.completions.create(
    model="massgen-multi",
    messages=[{"role": "user", "content": "Write a story"}],
    extra_body={
        "agent_models": ["gpt-4", "claude-3-opus", "gemini-pro"],
        "algorithm": "massgen",
        "consensus_threshold": 0.4  # Lower threshold for creativity
    }
)

# For factual tasks
factual_response = client.chat.completions.create(
    model="massgen-multi",
    messages=[{"role": "user", "content": "What is the speed of light?"}],
    extra_body={
        "agent_models": ["gpt-4", "claude-3", "gemini-pro"],
        "algorithm": "treequest",
        "consensus_threshold": 0.9  # Higher threshold for accuracy
    }
)
```

### Streaming with Multiple Agents

```python
stream = client.chat.completions.create(
    model="massgen-multi",
    messages=[{"role": "user", "content": "Explain machine learning"}],
    stream=True,
    extra_body={
        "agent_models": ["gpt-4", "claude-3"],
        "algorithm": "massgen"
    }
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Integration Examples

### LangChain Integration

```python
from langchain.chat_models import ChatOpenAI

# Use MassGen as a LangChain chat model
chat = ChatOpenAI(
    openai_api_base="http://localhost:8000/v1",
    openai_api_key="not-needed",
    model_name="massgen-multi",
    model_kwargs={
        "agent_models": ["gpt-4", "claude-3"],
        "consensus_threshold": 0.7
    }
)

response = chat.predict("What is the meaning of life?")
```

### AutoGen Integration

```python
import autogen

# Configure AutoGen to use MassGen
config_list = [{
    "model": "massgen-multi",
    "api_base": "http://localhost:8000/v1",
    "api_key": "not-needed"
}]

assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list}
)
```

## Performance Considerations

1. **Response Time**: Multi-agent consensus takes longer than single model calls
2. **Cost**: Using multiple models increases API costs proportionally
3. **Streaming**: Provides better user experience for long responses
4. **Caching**: Consider implementing response caching for repeated queries

## Error Handling

The API returns errors in OpenAI's format:

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": 500
  }
}
```

Common errors:
- Missing required fields (422)
- Invalid model names (400)
- Agent initialization failures (500)
- Consensus timeout (504)

## Security

1. **API Keys**: Store your provider API keys securely
2. **CORS**: Configure CORS settings for production
3. **Rate Limiting**: Implement rate limiting for public endpoints
4. **Authentication**: Add authentication layer if needed

## Monitoring

The `massgen_metadata` field provides insights into:
- Consensus achievement
- Number of debate rounds
- Representative agent selection
- Processing duration
- Algorithm used

Use these metrics to optimize your configuration and monitor system performance.