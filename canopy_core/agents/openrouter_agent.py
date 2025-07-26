# Agent extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen
# Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)
"""
OpenRouter agent implementation for accessing models like DeepSeek R1.

This module provides an agent that can interface with OpenRouter's API
to access various models including DeepSeek R1.
"""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

from openai import OpenAI

from ..types import AgentMessage, ModelConfig
from .base import BaseAgent

logger = logging.getLogger(__name__)


class OpenRouterAgent(BaseAgent):
    """Agent for OpenRouter API models including DeepSeek R1."""

    def __init__(
        self,
        agent_id: int,
        model_config: ModelConfig,
        orchestrator: Any,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Initialize OpenRouter agent.

        Args:
            agent_id: Unique identifier for this agent
            model_config: Configuration for the model
            orchestrator: Reference to the orchestrator
            stream_callback: Optional callback for streaming output
        """
        super().__init__(agent_id, model_config, orchestrator, stream_callback)

        # Set up OpenRouter client
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY or OPENROUTER_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

        # Map model names to OpenRouter model IDs
        self.model_mapping = {
            "deepseek-r1": "deepseek/deepseek-r1",
            "deepseek-r1-0528": "deepseek/deepseek-r1-0528",
            "openrouter/deepseek/deepseek-r1": "deepseek/deepseek-r1",
            "openrouter/deepseek/deepseek-r1-0528": "deepseek/deepseek-r1-0528",
        }

        # Get the actual model ID
        self.model_id = self.model_mapping.get(self.model, self.model)

        logger.info(f"📡 Initialized OpenRouter agent {agent_id} with model {self.model_id}")

    def process_message(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> AgentMessage:
        """Process messages using OpenRouter API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            tools: Optional tools (not supported by all models)
            **kwargs: Additional arguments passed to the API

        Returns:
            AgentMessage containing the response
        """
        try:
            # Prepare API call parameters
            params = {
                "model": self.model_id,
                "messages": messages,
                "temperature": temperature or self.model_config.temperature,
                "max_tokens": max_tokens or self.model_config.max_tokens,
            }

            # Add tools if provided and model supports them
            if tools and self._supports_tools():
                params["tools"] = tools
                params["tool_choice"] = kwargs.get("tool_choice", "auto")

            # Add any additional parameters
            for key in ["top_p", "frequency_penalty", "presence_penalty"]:
                if key in kwargs:
                    params[key] = kwargs[key]

            # Add OpenRouter-specific headers
            params["extra_headers"] = {
                "HTTP-Referer": "https://github.com/basitmustafa/canopy",
                "X-Title": "MassGen Canopy Benchmarks",
            }

            # Make API call
            if self.stream_callback:
                # Streaming response
                stream = self.client.chat.completions.create(**params, stream=True)

                full_content = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content
                        self.stream_callback(content)

                return AgentMessage(text=full_content, code=[], citations=[])
            else:
                # Non-streaming response
                response = self.client.chat.completions.create(**params)

                message = response.choices[0].message

                # Handle tool calls if present
                if hasattr(message, "tool_calls") and message.tool_calls:
                    # Process tool calls (placeholder)
                    logger.info(f"Tool calls received: {len(message.tool_calls)}")

                return AgentMessage(text=message.content or "", code=[], citations=[])

        except Exception as e:
            logger.error(f"❌ OpenRouter API error for agent {self.agent_id}: {str(e)}")
            raise RuntimeError(f"OpenRouter API error: {str(e)}")

    def _supports_tools(self) -> bool:
        """Check if the model supports function/tool calling."""
        # DeepSeek R1 models generally support tool calling
        # but we can expand this check as needed
        tool_supporting_models = ["deepseek/deepseek-r1", "deepseek/deepseek-r1-0528"]
        return self.model_id in tool_supporting_models

    @property
    def agent_type(self) -> str:
        """Return the agent type identifier."""
        return "openrouter"

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        info = super().get_info()
        info.update(
            {
                "api": "openrouter",
                "model_id": self.model_id,
                "supports_tools": self._supports_tools(),
            }
        )
        return info
