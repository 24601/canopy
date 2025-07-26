# ⏱️ 5-Minute Quick Start

Get Canopy running in 5 minutes or less! This streamlined guide gets you from zero to multi-agent consensus.

## 🏃 Speed Run Setup

### 1️⃣ Install (30 seconds)

```bash
# Clone and install
git clone https://github.com/yourusername/canopy.git && cd canopy
pip install -e .
```

### 2️⃣ Configure (1 minute)

```bash
# Create .env file with your API key
echo "OPENROUTER_API_KEY=your_key_here" > .env

# Don't have an API key? Get one free at:
# https://openrouter.ai/
```

### 3️⃣ First Query (30 seconds)

```bash
# Ask a question with multiple agents
python -m canopy "What's the best way to learn Python?" \
  --models gpt-4o-mini claude-3-haiku
```

### 4️⃣ Try the API Server (2 minutes)

```bash
# Terminal 1: Start the server
python -m canopy --serve

# Terminal 2: Make a request
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "canopy-multi",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 5️⃣ Interactive Mode (1 minute)

```bash
# Start chatting with multiple AI agents
python -m canopy --models gpt-4o-mini gemini-flash --interactive
```

## 🎯 That's It!

You now have:
- ✅ Multi-agent consensus system running
- ✅ API server for integrations
- ✅ Interactive chat with AI collaboration

## 🚀 What's Next?

### Try These Commands:

```bash
# Use more agents for complex questions
python -m canopy "Explain blockchain like I'm 5" \
  --models gpt-4o claude-3-sonnet gemini-pro mixtral-8x7b

# Use the beautiful TUI
python -m canopy --models gpt-4o claude-3-haiku --tui

# Use a pre-built configuration
python -m canopy --config examples/fast_config.yaml "Your question"
```

### Quick Examples:

**Code Review:**
```bash
python -m canopy "Review: def fib(n): return fib(n-1) + fib(n-2)" \
  --models gpt-4o claude-3-sonnet
```

**Creative Task:**
```bash
python -m canopy "Write a joke about programmers" \
  --models gpt-4o claude-3-haiku gemini-flash \
  --algorithm creative
```

**Analysis:**
```bash
python -m canopy "Compare Python vs JavaScript for web development" \
  --models gpt-4o claude-3-sonnet gemini-pro \
  --algorithm analytical
```

## 💡 Tips for Speed

1. **Use `--models` shorthand**:
   ```bash
   # These are equivalent
   --models gpt-4o claude-3-haiku
   -m gpt-4o claude-3-haiku
   ```

2. **Save configurations**:
   ```bash
   # Create your favorite setup
   cp examples/fast_config.yaml my_setup.yaml
   # Edit my_setup.yaml with your preferred models
   # Use it anytime:
   python -m canopy -c my_setup.yaml "Question"
   ```

3. **Alias for convenience**:
   ```bash
   # Add to your .bashrc or .zshrc
   alias canopy="python -m canopy"
   # Now just use:
   canopy "Your question" -m gpt-4o claude-3-haiku
   ```

## 🔥 Quick Wins

- **Fastest setup**: Use OpenRouter for all models with one key
- **Fastest models**: `gpt-4o-mini`, `claude-3-haiku`, `gemini-flash`
- **Fastest config**: Use `examples/fast_config.yaml`
- **Fastest feedback**: Use `--tui` for real-time visualization

---

**Done in 5 minutes?** 🎉 Check out the [full guide](README.md) for more features!
