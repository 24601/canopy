#!/usr/bin/env python3
"""
Example script demonstrating how to use the MassGen OpenAI-compatible API server.

Prerequisites:
1. Start the API server: python cli.py --serve
2. Ensure you have API keys configured in your .env file
3. Install the OpenAI client: pip install openai
"""

from openai import OpenAI


def basic_chat_example(client: OpenAI) -> None:
    """Basic chat completion example."""
    print("\n=== Basic Chat Completion ===")

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of Japan?"},
        ],
        temperature=0.7,
    )

    print(f"Response: {response.choices[0].message.content}")
    print(f"Tokens used: {response.usage.total_tokens}")


def multi_agent_chat_example(client: OpenAI) -> None:
    """Multi-agent consensus chat example."""
    print("\n=== Multi-Agent Chat Completion ===")

    response = client.chat.completions.create(
        model="massgen-multi",
        messages=[
            {
                "role": "user",
                "content": "What are the ethical implications of artificial general intelligence?",
            }
        ],
        extra_body={
            "agent_models": ["gpt-4", "claude-3-opus", "gemini-pro"],
            "consensus_threshold": 0.75,
            "max_debate_rounds": 3,
            "algorithm": "massgen",
        },
    )

    print(f"Response: {response.choices[0].message.content}")

    # Access MassGen metadata if available
    if hasattr(response, "massgen_metadata"):
        metadata = response.massgen_metadata
        print(f"\nConsensus reached: {metadata.get('consensus_reached')}")
        print(f"Representative agent: {metadata.get('representative_agent')}")
        print(f"Total agents: {metadata.get('total_agents')}")
        print(f"Debate rounds: {metadata.get('debate_rounds')}")


def streaming_example(client: OpenAI) -> None:
    """Streaming chat completion example."""
    print("\n=== Streaming Chat Completion ===")

    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Write a haiku about artificial intelligence"}],
        stream=True,
        extra_body={"agent_models": ["gpt-4", "claude-3"], "algorithm": "massgen"},
    )

    print("Streaming response: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()


def text_completion_example(client: OpenAI) -> None:
    """Text completion example."""
    print("\n=== Text Completion ===")

    # Note: OpenAI client v1.0+ doesn't have native completions support
    # You would need to use requests directly or downgrade to v0.28
    import requests

    response = requests.post(
        "http://localhost:8000/v1/completions",
        json={
            "model": "gpt-4",
            "prompt": "The three laws of robotics are:",
            "max_tokens": 100,
            "temperature": 0.5,
            "agent_models": ["gpt-4", "claude-3"],
            "consensus_threshold": 0.66,
        },
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Completion: {data['choices'][0]['text']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def treequest_example(client: OpenAI) -> None:
    """Example using TreeQuest algorithm."""
    print("\n=== TreeQuest Algorithm Example ===")

    response = client.chat.completions.create(
        model="massgen-multi",
        messages=[
            {
                "role": "user",
                "content": "Solve this step by step: If a train travels at 60 mph for 2.5 hours, how far does it go?",
            }
        ],
        extra_body={
            "agent_models": ["gpt-4", "gemini-pro"],
            "algorithm": "treequest",
            "consensus_threshold": 0.8,
        },
    )

    print(f"Response: {response.choices[0].message.content}")


def conversation_example(client: OpenAI) -> None:
    """Multi-turn conversation example."""
    print("\n=== Multi-turn Conversation ===")

    messages = [
        {"role": "system", "content": "You are a knowledgeable science tutor."},
        {"role": "user", "content": "What is photosynthesis?"},
    ]

    # First turn
    response = client.chat.completions.create(
        model="massgen-multi",
        messages=messages,
        extra_body={"agent_models": ["gpt-4", "claude-3"], "consensus_threshold": 0.66},
    )

    print(f"User: {messages[-1]['content']}")
    print(f"Assistant: {response.choices[0].message.content}")

    # Add response to conversation
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    messages.append({"role": "user", "content": "How does it relate to cellular respiration?"})

    # Second turn
    response = client.chat.completions.create(
        model="massgen-multi",
        messages=messages,
        extra_body={"agent_models": ["gpt-4", "claude-3"], "consensus_threshold": 0.66},
    )

    print(f"\nUser: {messages[-1]['content']}")
    print(f"Assistant: {response.choices[0].message.content}")


def list_models_example() -> None:
    """List available models example."""
    print("\n=== List Available Models ===")

    import requests

    response = requests.get("http://localhost:8000/v1/models")

    if response.status_code == 200:
        models = response.json()["data"]
        for model in models:
            print(f"- {model['id']} (owned by: {model['owned_by']})")
    else:
        print(f"Error: {response.status_code}")


def error_handling_example(client: OpenAI) -> None:
    """Example of error handling."""
    print("\n=== Error Handling Example ===")

    try:
        # This might fail if the model doesn't exist
        response = client.chat.completions.create(
            model="non-existent-model", messages=[{"role": "user", "content": "Test"}]
        )
    except Exception as e:
        print(f"Error caught: {type(e).__name__}: {e}")

    # With proper error handling
    try:
        response = client.chat.completions.create(
            model="massgen-multi",
            messages=[{"role": "user", "content": "Explain quantum computing"}],
            extra_body={
                "agent_models": ["gpt-4", "claude-3", "gemini-pro"],
                "consensus_threshold": 0.9,  # High threshold
                "max_debate_rounds": 5,
            },
            timeout=60.0,  # 60 second timeout
        )
        print(f"Success! Response length: {len(response.choices[0].message.content)} chars")
    except Exception as e:
        print(f"Error: {e}")


def creative_vs_factual_example(client: OpenAI) -> None:
    """Example showing different configurations for creative vs factual tasks."""
    print("\n=== Creative vs Factual Tasks ===")

    # Creative task - lower consensus threshold
    print("\nCreative Task:")
    creative_response = client.chat.completions.create(
        model="massgen-multi",
        messages=[
            {
                "role": "user",
                "content": "Write a creative story opening about a time traveler",
            }
        ],
        temperature=0.9,
        extra_body={
            "agent_models": ["gpt-4", "claude-3-opus"],
            "consensus_threshold": 0.4,  # Lower threshold for diversity
            "algorithm": "massgen",
        },
    )
    print(creative_response.choices[0].message.content[:200] + "...")

    # Factual task - higher consensus threshold
    print("\nFactual Task:")
    factual_response = client.chat.completions.create(
        model="massgen-multi",
        messages=[
            {
                "role": "user",
                "content": "What is the exact value of the speed of light in vacuum?",
            }
        ],
        temperature=0.1,
        extra_body={
            "agent_models": ["gpt-4", "claude-3", "gemini-pro"],
            "consensus_threshold": 0.9,  # High threshold for accuracy
            "algorithm": "treequest",
        },
    )
    print(factual_response.choices[0].message.content)


def main():
    """Run all examples."""
    # Initialize client pointing to MassGen server
    client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")  # MassGen uses configured provider keys

    print("MassGen API Client Examples")
    print("=" * 50)

    # Check if server is running
    import requests

    try:
        health = requests.get("http://localhost:8000/health")
        if health.status_code != 200:
            print("❌ Error: MassGen API server is not running!")
            print("Start it with: python cli.py --serve")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to MassGen API server!")
        print("Start it with: python cli.py --serve")
        return

    print("✅ Connected to MassGen API server")

    # Run examples
    try:
        basic_chat_example(client)
        multi_agent_chat_example(client)
        streaming_example(client)
        text_completion_example(client)
        treequest_example(client)
        conversation_example(client)
        list_models_example()
        creative_vs_factual_example(client)
        error_handling_example(client)
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")

    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    main()
