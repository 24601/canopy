# Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)
"""
OpenRouter configuration helpers for MassGen.

This module provides helpers for configuring agents that use OpenRouter API,
particularly for accessing models like DeepSeek R1.
"""

from typing import List

from .types import AgentConfig, ModelConfig


def create_openrouter_agent_config(
    agent_id: int,
    model: str = "deepseek/deepseek-r1",
    temperature: float = 0.7,
    max_tokens: int = 8192,
    **kwargs,
) -> AgentConfig:
    """Create an agent configuration for OpenRouter models.

    Args:
        agent_id: Unique identifier for the agent
        model: Model name (e.g., "deepseek/deepseek-r1", "deepseek/deepseek-r1-0528")
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        **kwargs: Additional model configuration

    Returns:
        AgentConfig for OpenRouter agent
    """
    model_config = ModelConfig(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)

    return AgentConfig(agent_id=agent_id, agent_type="openrouter", model_config=model_config)


def get_deepseek_r1_config(agent_id: int, version: str = "latest", temperature: float = 0.7, **kwargs) -> AgentConfig:
    """Get configuration for DeepSeek R1 model.

    Args:
        agent_id: Unique identifier for the agent
        version: Version of DeepSeek R1 ("latest" or "0528")
        temperature: Temperature for generation
        **kwargs: Additional configuration

    Returns:
        AgentConfig for DeepSeek R1
    """
    model_map = {"latest": "deepseek/deepseek-r1", "0528": "deepseek/deepseek-r1-0528"}

    model = model_map.get(version, "deepseek/deepseek-r1")

    return create_openrouter_agent_config(agent_id=agent_id, model=model, temperature=temperature, **kwargs)


def create_sakana_benchmark_agents(num_agents: int = 3) -> List[AgentConfig]:
    """Create agent configurations matching Sakana AI's benchmark setup.

    This creates a mix of agents including:
    - GPT-4o-mini
    - Gemini 2.5 Pro
    - DeepSeek R1

    Args:
        num_agents: Number of agents to create (default 3)

    Returns:
        List of agent configurations
    """
    configs = []

    # Agent 1: GPT-4o-mini
    if num_agents >= 1:
        configs.append(
            AgentConfig(
                agent_id=1,
                agent_type="openai",
                model_config=ModelConfig(model="gpt-4o-mini", temperature=0.6, max_tokens=8192),
            )
        )

    # Agent 2: Gemini 2.5 Pro
    if num_agents >= 2:
        configs.append(
            AgentConfig(
                agent_id=2,
                agent_type="gemini",
                model_config=ModelConfig(model="gemini-2.5-pro", temperature=0.6, max_tokens=8192),
            )
        )

    # Agent 3: DeepSeek R1 via OpenRouter
    if num_agents >= 3:
        configs.append(get_deepseek_r1_config(agent_id=3, version="0528", temperature=0.6))

    # Additional agents cycle through the models
    for i in range(3, num_agents):
        agent_id = i + 1
        if i % 3 == 0:
            # GPT-4o-mini
            configs.append(
                AgentConfig(
                    agent_id=agent_id,
                    agent_type="openai",
                    model_config=ModelConfig(model="gpt-4o-mini", temperature=0.6),
                )
            )
        elif i % 3 == 1:
            # Gemini
            configs.append(
                AgentConfig(
                    agent_id=agent_id,
                    agent_type="gemini",
                    model_config=ModelConfig(model="gemini-2.5-pro", temperature=0.6),
                )
            )
        else:
            # DeepSeek
            configs.append(get_deepseek_r1_config(agent_id=agent_id, temperature=0.6))

    return configs
