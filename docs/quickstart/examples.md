# 📚 Quick Start Examples

Ready-to-run examples to get you started with Canopy's multi-agent system.

## 🎯 Basic Examples

### 1. Simple Question Answering

```bash
# Ask a straightforward question
python -m canopy "What are the benefits of exercise?" \
  --models gpt-4o-mini claude-3-haiku

# With specific algorithm
python -m canopy "Explain photosynthesis" \
  --models gpt-4o claude-3-sonnet \
  --algorithm analytical
```

### 2. Code Analysis

```python
# code_review.py
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

response = client.chat.completions.create(
    model="canopy-multi",
    messages=[
        {"role": "system", "content": "You are a code reviewer."},
        {"role": "user", "content": f"Review this code:\n\n{code}"}
    ],
    extra_body={
        "agent_models": ["gpt-4o", "claude-3-sonnet"],
        "algorithm": "analytical"
    }
)

print(response.choices[0].message.content)
```

### 3. Creative Writing

```bash
# Story writing with creative algorithm
python -m canopy "Write a short story about a time traveler" \
  --models gpt-4o claude-3-opus gemini-pro \
  --algorithm creative \
  --consensus 0.6  # Lower threshold for more variety
```

## 💡 Advanced Examples

### 4. Multi-Turn Conversation

```python
# conversation.py
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

messages = [
    {"role": "system", "content": "You are a helpful tutor."},
    {"role": "user", "content": "Explain machine learning"}
]

# First turn
response = client.chat.completions.create(
    model="canopy-multi",
    messages=messages,
    extra_body={"agent_models": ["gpt-4o", "claude-3-sonnet"]}
)

print("AI:", response.choices[0].message.content)

# Add response to conversation
messages.append({"role": "assistant", "content": response.choices[0].message.content})
messages.append({"role": "user", "content": "Can you give me a simple example?"})

# Second turn
response = client.chat.completions.create(
    model="canopy-multi",
    messages=messages,
    extra_body={"agent_models": ["gpt-4o", "claude-3-sonnet"]}
)

print("AI:", response.choices[0].message.content)
```

### 5. Streaming with Progress

```python
# streaming_example.py
from openai import OpenAI
import sys

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

print("Agents thinking", end="")

stream = client.chat.completions.create(
    model="canopy-multi",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    stream=True,
    extra_body={
        "agent_models": ["gpt-4o", "claude-3-sonnet", "gemini-pro"],
        "stream_consensus": True
    }
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        if "Agents thinking" in chunk.choices[0].delta.content:
            print(".", end="")
            sys.stdout.flush()
        else:
            print("\n" if "consensus" in chunk.choices[0].delta.content.lower() else "", end="")
            print(chunk.choices[0].delta.content, end="")
```

### 6. Comparative Analysis

```python
# compare.py
from canopy import Canopy

# Initialize with specific models for comparison
canopy = Canopy(models=["gpt-4o", "claude-3-sonnet", "gemini-pro"])

# Ask for comparative analysis
result = canopy.analyze(
    "Compare the environmental impact of electric vs gasoline vehicles",
    algorithm="analytical",
    include_individual_responses=True
)

# Show individual agent perspectives
for agent in result.agent_responses:
    print(f"\n{agent.model} perspective:")
    print(agent.response)

print(f"\nConsensus ({result.consensus_score:.0%} agreement):")
print(result.consensus)
```

## 🔧 Utility Scripts

### 7. Batch Processing

```python
# batch_process.py
import json
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

# Questions to process
questions = [
    "What is artificial intelligence?",
    "How does machine learning work?",
    "What are neural networks?",
    "Explain deep learning"
]

results = []

for question in questions:
    print(f"Processing: {question}")
    response = client.chat.completions.create(
        model="canopy-multi",
        messages=[{"role": "user", "content": question}],
        extra_body={
            "agent_models": ["gpt-4o-mini", "claude-3-haiku"],
            "algorithm": "fast"  # Use fast algorithm for batch
        }
    )

    results.append({
        "question": question,
        "answer": response.choices[0].message.content
    })

# Save results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### 8. Model Comparison Tool

```python
# model_compare.py
import time
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

def compare_models(question, model_sets):
    results = {}

    for name, models in model_sets.items():
        start = time.time()

        response = client.chat.completions.create(
            model="canopy-multi",
            messages=[{"role": "user", "content": question}],
            extra_body={"agent_models": models}
        )

        results[name] = {
            "response": response.choices[0].message.content,
            "time": time.time() - start,
            "tokens": response.usage.total_tokens
        }

    return results

# Compare different model combinations
comparisons = compare_models(
    "What is the meaning of life?",
    {
        "fast": ["gpt-4o-mini", "claude-3-haiku"],
        "balanced": ["gpt-4o", "claude-3-sonnet"],
        "powerful": ["gpt-4o", "claude-3-opus", "gemini-ultra"]
    }
)

for name, result in comparisons.items():
    print(f"\n{name.upper()} ({result['time']:.2f}s, {result['tokens']} tokens):")
    print(result['response'][:200] + "...")
```

## 🎨 Interactive Examples

### 9. Terminal Chat Interface

```python
# chat.py
from openai import OpenAI
import readline  # For better input handling

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

print("🌳 Canopy Multi-Agent Chat")
print("Type 'quit' to exit, 'clear' to reset conversation")
print("-" * 50)

messages = []

while True:
    try:
        user_input = input("\nYou: ")

        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            messages = []
            print("Conversation cleared!")
            continue

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="canopy-multi",
            messages=messages,
            extra_body={
                "agent_models": ["gpt-4o", "claude-3-sonnet"],
                "algorithm": "balanced"
            }
        )

        ai_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_response})

        print(f"\nAI: {ai_response}")

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        break
    except Exception as e:
        print(f"\nError: {e}")
```

### 10. Gradio Web Interface

```python
# web_interface.py
import gradio as gr
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

def chat_with_agents(message, model1, model2, model3, algorithm):
    models = [m for m in [model1, model2, model3] if m]

    if not models:
        return "Please select at least one model!"

    response = client.chat.completions.create(
        model="canopy-multi",
        messages=[{"role": "user", "content": message}],
        extra_body={
            "agent_models": models,
            "algorithm": algorithm
        }
    )

    return response.choices[0].message.content

# Create Gradio interface
interface = gr.Interface(
    fn=chat_with_agents,
    inputs=[
        gr.Textbox(label="Your Question", lines=3),
        gr.Dropdown(["gpt-4o", "gpt-4o-mini", ""], label="Model 1", value="gpt-4o"),
        gr.Dropdown(["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", ""], label="Model 2", value="claude-3-sonnet"),
        gr.Dropdown(["gemini-ultra", "gemini-pro", "gemini-flash", ""], label="Model 3", value=""),
        gr.Radio(["balanced", "analytical", "creative", "fast"], label="Algorithm", value="balanced")
    ],
    outputs=gr.Textbox(label="Consensus Response", lines=10),
    title="🌳 Canopy Multi-Agent Consensus",
    description="Ask questions and get consensus answers from multiple AI models"
)

if __name__ == "__main__":
    interface.launch()
```

## 🚀 Quick Copy-Paste Starters

### For Analysis Tasks

```bash
python -m canopy "Analyze the pros and cons of remote work" \
  --models gpt-4o claude-3-sonnet gemini-pro \
  --algorithm analytical \
  --output analysis.md
```

### For Creative Tasks

```bash
python -m canopy "Write a creative product description for eco-friendly water bottles" \
  --models gpt-4o claude-3-opus gemini-pro \
  --algorithm creative \
  --consensus 0.6
```

### For Quick Decisions

```bash
python -m canopy "Should I learn Python or JavaScript first?" \
  --models gpt-4o-mini claude-3-haiku gemini-flash \
  --algorithm fast \
  --max-rounds 1
```

### For Complex Problems

```bash
python -m canopy "Design a scalable microservices architecture for an e-commerce platform" \
  --models gpt-4o claude-3-opus gemini-ultra \
  --algorithm treequest \
  --max-duration 300
```

## 📝 Configuration Examples

### Fast Response Config

```yaml
# fast.yaml
orchestrator:
  consensus_threshold: 0.5
  max_debate_rounds: 1
  max_duration: 60

agents:
  - agent_type: openai
    model_config:
      model: gpt-4o-mini
      temperature: 0.7
  - agent_type: anthropic
    model_config:
      model: claude-3-haiku
      temperature: 0.7
```

### High Quality Config

```yaml
# quality.yaml
orchestrator:
  consensus_threshold: 0.9
  max_debate_rounds: 5
  max_duration: 300

agents:
  - agent_type: openai
    model_config:
      model: gpt-4o
      temperature: 0.5
  - agent_type: anthropic
    model_config:
      model: claude-3-opus
      temperature: 0.5
  - agent_type: google
    model_config:
      model: gemini-ultra
      temperature: 0.5
```

---

**Want more examples?** Check out the [examples directory](../../examples/) or [contribute your own](../../CONTRIBUTING.md)!
