# 🚀 Canopy Quick Start Guide

Get up and running with Canopy in under 5 minutes! This guide will help you install, configure, and start using Canopy's multi-agent consensus system.

## 📋 Prerequisites

- Python 3.10 or higher
- An API key from at least one supported provider:
  - [OpenRouter](https://openrouter.ai/) (Recommended - access to multiple models)
  - [OpenAI](https://platform.openai.com/)
  - [Anthropic](https://console.anthropic.com/)
  - [Google AI Studio](https://makersuite.google.com/app/apikey)
  - [xAI](https://x.ai/)

## ⚡ Installation

### Option 1: Using pip (Recommended)

```bash
# Install Canopy
pip install canopy

# Or install from source
git clone https://github.com/yourusername/canopy.git
cd canopy
pip install -e .
```

### Option 2: Using uv (Faster)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Canopy
git clone https://github.com/yourusername/canopy.git
cd canopy
uv pip install -e .
```

## 🔑 Configuration

### Step 1: Set up API Keys

Create a `.env` file in your project directory:

```bash
# Option 1: Use OpenRouter for access to all models (Recommended)
OPENROUTER_API_KEY=your_openrouter_key_here

# Option 2: Use individual provider keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GEMINI_API_KEY=your_gemini_key_here
XAI_API_KEY=your_xai_key_here
```

### Step 2: Verify Installation

```bash
# Test with a simple query
python -m canopy "What is 2+2?" --models gpt-4o-mini

# You should see agents working together to answer your question
```

## 🎯 Basic Usage

### 1. Simple Multi-Agent Query

```bash
# Use multiple models to answer a question
python -m canopy "Explain quantum computing in simple terms" \
  --models gpt-4o claude-3-haiku gemini-flash
```

### 2. Using Configuration Files

```bash
# Use a pre-configured setup for fast responses
python -m canopy --config examples/fast_config.yaml \
  "What are the benefits of renewable energy?"
```

### 3. Interactive Mode

```bash
# Start an interactive session
python -m canopy --models gpt-4o claude-3-haiku --interactive

# Now you can have a conversation with multiple agents
> What's the best programming language for beginners?
# Agents will discuss and reach consensus
> Why do you recommend that?
# Follow-up questions maintain context
```

## 🌐 API Server Mode

### Start the Server

```bash
# Launch the OpenAI-compatible API server
python -m canopy --serve

# Server starts at http://localhost:8000
```

### Use with Python

```python
from openai import OpenAI

# Connect to Canopy server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # No API key required for local server
)

# Make a request with multiple agents
response = client.chat.completions.create(
    model="canopy-multi",
    messages=[
        {"role": "user", "content": "What's the meaning of life?"}
    ],
    extra_body={
        "agent_models": ["gpt-4o", "claude-3-sonnet", "gemini-pro"],
        "consensus_threshold": 0.75
    }
)

print(response.choices[0].message.content)
```

### Use with curl

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "canopy-multi",
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "agent_models": ["gpt-4o-mini", "claude-3-haiku"]
  }'
```

## 🎨 Terminal UI

Canopy includes a beautiful terminal interface powered by Textual:

```bash
# Start with the TUI (Terminal User Interface)
python -m canopy --models gpt-4o claude-3-haiku --tui

# Features:
# - Real-time agent progress visualization
# - Color-coded agent responses
# - Consensus tracking
# - Interactive chat interface
```

## 🛠️ Common Use Cases

### 1. Code Review

```bash
python -m canopy "Review this Python code for best practices: \
def factorial(n): return 1 if n <= 1 else n * factorial(n-1)" \
--models gpt-4o claude-3-sonnet
```

### 2. Creative Writing

```bash
python -m canopy "Write a haiku about artificial intelligence" \
--models gpt-4o claude-3-haiku gemini-pro \
--algorithm creative
```

### 3. Technical Analysis

```bash
python -m canopy "Compare REST vs GraphQL for a mobile app backend" \
--models gpt-4o claude-3-sonnet gemini-pro \
--algorithm analytical
```

### 4. Problem Solving

```bash
python -m canopy "Design a scalable architecture for a social media platform" \
--models gpt-4o claude-3-opus gemini-ultra \
--algorithm treequest
```

## 📝 Configuration Options

### Command Line Arguments

```bash
python -m canopy [QUERY] [OPTIONS]

Options:
  --models          Space-separated list of models to use
  --config          Path to YAML configuration file
  --algorithm       Algorithm to use (massgen, treequest, creative, analytical)
  --consensus       Consensus threshold (0.0-1.0, default: 0.75)
  --max-rounds      Maximum debate rounds (default: 3)
  --interactive     Start interactive mode
  --serve           Start API server
  --tui             Use Terminal UI
  --output          Output format (text, json, markdown)
  --verbose         Enable verbose logging
```

### Available Models

When using OpenRouter (recommended):
- `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`
- `gemini-pro`, `gemini-flash`, `gemini-ultra`
- `mixtral-8x7b`, `mistral-large`
- `llama-3-70b`, `llama-3-8b`

## 🔧 Advanced Configuration

Create a custom configuration file (`my_config.yaml`):

```yaml
orchestrator:
  max_duration: 300
  consensus_threshold: 0.8
  max_debate_rounds: 5
  algorithm: treequest

agents:
  - agent_id: 1
    agent_type: openai
    model_config:
      model: gpt-4o
      temperature: 0.7
      max_tokens: 2000

  - agent_id: 2
    agent_type: anthropic
    model_config:
      model: claude-3-sonnet
      temperature: 0.5

  - agent_id: 3
    agent_type: gemini
    model_config:
      model: gemini-pro
      temperature: 0.8

display:
  theme: monokai
  show_thinking: true
  show_consensus: true
```

Use your custom config:

```bash
python -m canopy --config my_config.yaml "Your question here"
```

## 🐛 Troubleshooting

### Common Issues

1. **"No API keys found"**
   ```bash
   # Make sure your .env file is in the current directory
   # Or set environment variables directly:
   export OPENROUTER_API_KEY=your_key_here
   ```

2. **"Model not available"**
   ```bash
   # Check available models for your API keys
   python -m canopy --list-models
   ```

3. **"Import error"**
   ```bash
   # Ensure all dependencies are installed
   pip install -e ".[all]"
   ```

### Getting Help

```bash
# Show help message
python -m canopy --help

# Check version
python -m canopy --version

# Run diagnostics
python -m canopy --diagnose
```

## 🎉 Next Steps

Now that you're up and running:

1. **Explore Examples**: Check out the `examples/` directory for more use cases
2. **Read the Docs**: See the [full documentation](../README.md) for advanced features
3. **Join the Community**: Star us on GitHub and join our Discord
4. **Contribute**: We welcome contributions! See [CONTRIBUTING.md](../../CONTRIBUTING.md)

## 💡 Pro Tips

1. **Use OpenRouter**: It provides access to multiple models with a single API key
2. **Start Small**: Begin with 2-3 models before scaling up
3. **Experiment with Algorithms**: Different algorithms work better for different tasks
4. **Monitor Costs**: Use `--dry-run` to estimate API costs before running
5. **Save Conversations**: Use `--output conversation.json` to save for later

---

**Need more help?** Check our [FAQ](../faq.md) or [open an issue](https://github.com/yourusername/canopy/issues)!
