# Canopy A2A (Agent-to-Agent) Protocol

Canopy implements the A2A (Agent-to-Agent) protocol, enabling standardized communication between AI agents and integration with A2A-compatible systems.

## Overview

The A2A protocol provides:
- Standardized agent discovery through agent cards
- Structured message formats for inter-agent communication
- Capability negotiation and parameter passing
- Execution metadata and error handling

## Agent Card

Canopy exposes its capabilities through a standard A2A agent card:

```json
{
  "name": "Canopy Multi-Agent System",
  "description": "Multi-agent consensus system for collaborative problem-solving",
  "version": "1.0.0",
  "capabilities": [
    "multi-agent-consensus",
    "tree-based-exploration", 
    "parallel-processing",
    "model-agnostic",
    "streaming-responses",
    "structured-outputs"
  ],
  "supported_protocols": ["a2a/1.0", "openai-compatible", "mcp/1.0"],
  "supported_models": [
    "openai/gpt-4",
    "anthropic/claude-3",
    "google/gemini-pro",
    "xai/grok"
  ],
  "input_formats": ["text/plain", "application/json", "a2a/message"],
  "output_formats": ["text/plain", "application/json", "a2a/response"],
  "max_context_length": 128000,
  "supports_streaming": true,
  "supports_function_calling": true,
  "documentation_url": "https://github.com/yourusername/canopy"
}
```

## Usage

### Python Client

```python
from canopy.a2a_agent import CanopyA2AAgent

# Initialize agent
agent = CanopyA2AAgent(
    models=["gpt-4", "claude-3"],
    algorithm="treequest",
    consensus_threshold=0.75
)

# Get agent card
agent_card = agent.get_agent_card()
print(f"Agent: {agent_card['name']}")
print(f"Capabilities: {agent_card['capabilities']}")

# Process a request
response = agent.process_request(
    content="What are the key principles of distributed systems?",
    parameters={
        "models": ["gpt-4", "claude-3", "gemini-pro"],
        "algorithm": "massgen",
        "consensus_threshold": 0.8
    }
)

print(f"Answer: {response['content']}")
print(f"Consensus achieved: {response['consensus_achieved']}")
```

### A2A Message Format

Send messages in A2A format:

```python
message = {
    "protocol": "a2a/1.0",
    "message_id": "msg-123",
    "sender": {
        "name": "my-agent",
        "type": "assistant"
    },
    "content": "Explain machine learning",
    "parameters": {
        "models": ["gpt-4", "claude-3"],
        "algorithm": "treequest",
        "max_debate_rounds": 5
    }
}

response = agent.handle_a2a_message(message)
```

### Response Format

Responses follow the A2A response structure:

```json
{
  "protocol": "a2a/1.0",
  "correlation_id": "msg-123",
  "content": "Machine learning is...",
  "execution_time_ms": 3456,
  "consensus_achieved": true,
  "metadata": {
    "representative_agent": "agent_1",
    "total_agents": 3,
    "debate_rounds": 2,
    "vote_distribution": {
      "agent_0": 1,
      "agent_1": 2
    }
  }
}
```

## HTTP Endpoints

When running as a web service, Canopy exposes A2A endpoints:

### GET /agent
Returns the agent card with full capability information.

### GET /capabilities
Returns detailed capability information including available algorithms and configuration options.

### POST /message
Accepts A2A protocol messages and returns A2A responses.

**Request:**
```json
{
  "protocol": "a2a/1.0",
  "message_id": "unique-id",
  "content": "Your question here",
  "parameters": {
    "models": ["gpt-4", "claude-3"],
    "algorithm": "massgen"
  }
}
```

**Response:**
```json
{
  "protocol": "a2a/1.0",
  "correlation_id": "unique-id",
  "content": "The answer is...",
  "execution_time_ms": 2500,
  "consensus_achieved": true,
  "metadata": {...}
}
```

## Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
from canopy.a2a_agent import create_a2a_handlers

app = FastAPI()
handlers = create_a2a_handlers()

@app.get("/agent")
async def get_agent_card():
    return handlers["agent_card"]()

@app.post("/message")
async def handle_message(message: dict):
    return handlers["message"](message)
```

### With Other A2A Agents

```python
# Discover agent capabilities
agent_card = canopy_agent.get_agent_card()

# Check supported features
if "multi-agent-consensus" in agent_card["capabilities"]:
    # Use multi-agent features
    response = canopy_agent.process_request(
        "Complex question requiring consensus",
        parameters={"models": ["gpt-4", "claude-3", "gemini-pro"]}
    )
```

## Configuration Options

### Models
Specify which AI models to use:
```python
parameters={"models": ["gpt-4", "claude-3", "gemini-pro"]}
```

### Algorithm
Choose consensus algorithm:
```python
parameters={"algorithm": "massgen"}  # or "treequest"
```

### Consensus Threshold
Set agreement threshold (0.0-1.0):
```python
parameters={"consensus_threshold": 0.75}
```

### Max Debate Rounds
Limit debate iterations:
```python
parameters={"max_debate_rounds": 5}
```

## Error Handling

Errors are returned in the A2A response format:

```json
{
  "protocol": "a2a/1.0",
  "correlation_id": "msg-123",
  "content": "Error processing request: Invalid model specified",
  "errors": ["Invalid model specified"]
}
```

## Best Practices

1. **Check Capabilities**: Always check the agent card before using advanced features
2. **Set Appropriate Thresholds**: Higher thresholds for factual queries, lower for creative tasks
3. **Handle Timeouts**: Multi-agent consensus can take time, set appropriate timeouts
4. **Monitor Metadata**: Use execution metadata to optimize performance
5. **Graceful Degradation**: Have fallbacks for when consensus isn't reached