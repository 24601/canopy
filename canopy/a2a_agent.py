"""
A2A (Agent-to-Agent) protocol implementation for Canopy.

This module provides an A2A-compatible agent interface following Google's
Agent-to-Agent Communication protocol, including agent card metadata.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from canopy_core.config import create_config_from_models
from canopy_core.main import run_mass_with_config

logger = logging.getLogger(__name__)


@dataclass
class Capability:
    """Capability definition for A2A protocol."""

    name: str
    description: str
    version: str = "1.0.0"
    parameters: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert capability to dictionary."""
        return asdict(self)


@dataclass
class AgentCard:
    """Agent card metadata following A2A protocol specification."""

    # Required fields
    name: str = "Canopy Multi-Agent System"
    description: str = "A multi-agent consensus system for collaborative problem-solving"
    version: str = "1.0.0"
    vendor: str = "Canopy Project"

    # Capabilities
    capabilities: List[str] = None
    supported_protocols: List[str] = None
    supported_models: List[str] = None

    # Interaction metadata
    input_formats: List[str] = None
    output_formats: List[str] = None
    max_context_length: int = 128000
    supports_streaming: bool = True
    supports_function_calling: bool = True

    # Resource requirements
    requires_api_keys: List[str] = None
    estimated_latency_ms: int = 5000

    # Contact and documentation
    documentation_url: str = "https://github.com/yourusername/canopy"
    contact_email: str = "support@canopy.ai"

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default values for list fields."""
        if self.capabilities is None:
            self.capabilities = [
                "multi-agent-consensus",
                "tree-based-exploration",
                "parallel-processing",
                "model-agnostic",
                "streaming-responses",
                "structured-outputs",
            ]

        if self.supported_protocols is None:
            self.supported_protocols = [
                "a2a/1.0",
                "openai-compatible",
                "mcp/1.0",
            ]

        if self.supported_models is None:
            self.supported_models = [
                "openai/gpt-4.1",
                "openai/gpt-4.1-mini",
                "openai/o4-mini",
                "openai/o3",
                "anthropic/claude-opus-4",
                "anthropic/claude-sonnet-4",
                "google/gemini-2.5-pro",
                "google/gemini-2.5-flash",
                "google/gemini-2.5-pro-deep-think",
                "xai/grok-4",
                "xai/grok-4-heavy",
            ]

        if self.input_formats is None:
            self.input_formats = [
                "text/plain",
                "application/json",
                "a2a/message",
            ]

        if self.output_formats is None:
            self.output_formats = [
                "text/plain",
                "application/json",
                "a2a/response",
            ]

        if self.requires_api_keys is None:
            self.requires_api_keys = [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GEMINI_API_KEY",
                "XAI_API_KEY",
                "OPENROUTER_API_KEY",
            ]

        if self.metadata is None:
            self.metadata = {
                "last_updated": "2025-01-25",
                "compatible_protocols": ["a2a/1.0", "mcp/1.0"],
                "performance_metrics": {
                    "avg_response_time_ms": self.estimated_latency_ms,
                    "context_length": self.max_context_length,
                    "streaming_supported": self.supports_streaming,
                },
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent card to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert agent card to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class A2AMessage:
    """A2A protocol message format."""

    # Core required fields
    id: str
    type: str  # "query", "capabilities", "info", etc.
    content: str
    sender_id: str
    timestamp: str

    # Optional metadata
    metadata: Optional[Dict[str, Any]] = None

    # Legacy fields for compatibility
    protocol: str = "a2a/1.0"
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None
    sender: Optional[Dict[str, str]] = None
    content_type: str = "text/plain"
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Handle legacy field mappings."""
        # Map message_id to id if needed
        if not self.message_id and self.id:
            self.message_id = self.id
        elif self.message_id and not hasattr(self, "id"):
            self.id = self.message_id

        # Map sender_id to sender dict if needed
        if self.sender_id and not self.sender:
            self.sender = {"id": self.sender_id, "type": "agent"}

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class A2AResponse:
    """A2A protocol response format."""

    # Core required fields
    request_id: str
    status: str  # "success", "error"
    content: str
    timestamp: str

    # Optional fields
    metadata: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    # Legacy fields for compatibility
    protocol: str = "a2a/1.0"
    message_id: Optional[str] = None
    correlation_id: Optional[str] = None
    content_type: str = "text/plain"
    execution_time_ms: Optional[int] = None
    model_used: Optional[str] = None
    consensus_achieved: Optional[bool] = None
    errors: Optional[List[str]] = None

    def __post_init__(self):
        """Handle legacy field mappings."""
        # Map correlation_id to request_id if needed
        if not self.request_id and self.correlation_id:
            self.request_id = self.correlation_id
        elif self.request_id and not self.correlation_id:
            self.correlation_id = self.request_id

        # Map errors list to error_message if needed
        if self.errors and not self.error_message:
            self.error_message = "; ".join(self.errors)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


class CanopyA2AAgent:
    """A2A-compatible agent for Canopy multi-agent system."""

    def __init__(
        self,
        models: Optional[List[str]] = None,
        algorithm: str = "massgen",
        consensus_threshold: float = 0.66,
        max_debate_rounds: int = 3,
        config: Optional[Any] = None,  # MassConfig type
    ):
        """Initialize the A2A agent.

        Args:
            models: List of models to use (defaults to latest 2025 models)
            algorithm: Consensus algorithm to use
            consensus_threshold: Threshold for consensus
            max_debate_rounds: Maximum debate rounds
            config: Optional MassConfig to use instead of creating from models
        """
        if config:
            # Extract values from config
            self.config = config
            self.models = [agent.model_config.model for agent in config.agents]
            self.algorithm = config.orchestrator.algorithm
            self.consensus_threshold = config.orchestrator.consensus_threshold
            self.max_debate_rounds = config.orchestrator.max_debate_rounds
        else:
            self.models = models or [
                "gpt-4.1",
                "claude-opus-4",
                "gemini-2.5-pro",
                "grok-4",
            ]
            self.algorithm = algorithm
            self.consensus_threshold = consensus_threshold
            self.max_debate_rounds = max_debate_rounds
            self.config = None

        self.agent_card = AgentCard()

    def get_agent_card(self) -> AgentCard:
        """Return the agent card."""
        return self.agent_card

    async def handle_message(self, message: A2AMessage) -> A2AResponse:
        """Handle an incoming A2A message (async).

        Args:
            message: A2A message object

        Returns:
            A2A response object
        """
        try:
            # Handle different message types
            if message.type == "capabilities":
                capabilities = self.get_capabilities()
                capabilities_dict = [cap.to_dict() for cap in capabilities]
                return A2AResponse(
                    request_id=message.id,
                    status="success",
                    content=json.dumps({"capabilities": capabilities_dict}),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

            elif message.type == "info":
                capabilities = self.get_capabilities()
                capabilities_dict = [cap.to_dict() for cap in capabilities]
                info = {
                    "agent_card": self.get_agent_card().to_dict(),
                    "capabilities": capabilities_dict,
                    "status": "ready",
                }
                return A2AResponse(
                    request_id=message.id,
                    status="success",
                    content=json.dumps(info),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

            elif message.type == "query":
                # Check for empty content
                if not message.content:
                    return A2AResponse(
                        request_id=message.id,
                        status="error",
                        content="",
                        error_code="empty_content",
                        error_message="Query content cannot be empty",
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )

                # Process the query using the sync method
                response_dict = await asyncio.to_thread(self._handle_query_sync, message)

                # Convert dict response to A2AResponse object
                return A2AResponse(
                    request_id=message.id,
                    status="success",
                    content=response_dict.get("content", ""),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    metadata=response_dict.get("metadata", {}),
                    execution_time_ms=response_dict.get("execution_time_ms"),
                    consensus_achieved=response_dict.get("consensus_achieved"),
                )

            else:
                return A2AResponse(
                    request_id=message.id,
                    status="error",
                    content="",
                    error_code="unknown_message_type",
                    error_message=f"Unknown message type: {message.type}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )

        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            return A2AResponse(
                request_id=message.id,
                status="error",
                content="",
                error_code="processing_error",
                error_message=str(e),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    def _handle_query_sync(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle query message synchronously."""
        # Extract parameters from metadata
        metadata = message.metadata or {}
        models = metadata.get("models", self.models)
        algorithm = metadata.get("algorithm", self.algorithm)
        consensus_threshold = metadata.get("consensus_threshold", self.consensus_threshold)
        max_debate_rounds = metadata.get("max_debate_rounds", self.max_debate_rounds)

        # Validate and adjust parameters
        if not models:
            models = self.models
        consensus_threshold = max(0.0, min(1.0, consensus_threshold))
        max_debate_rounds = max(1, max_debate_rounds)

        # Create configuration with display disabled for A2A usage
        config = create_config_from_models(
            models=models,
            orchestrator_config={
                "algorithm": algorithm,
                "consensus_threshold": consensus_threshold,
                "max_debate_rounds": max_debate_rounds,
            },
        )
        # Disable streaming display for A2A agent usage
        config.streaming_display.display_enabled = False

        # Run Canopy
        import time

        start_time = time.time()
        result = run_mass_with_config(message.content, config)
        execution_time = int((time.time() - start_time) * 1000)

        return {
            "content": result["answer"],
            "execution_time_ms": execution_time,
            "consensus_achieved": result.get("consensus_reached", False),
            "metadata": {
                "consensus_reached": result.get("consensus_reached", False),
                "confidence": result.get("confidence", 0.0),
                "representative_agent": result.get("representative_agent_id"),
                "total_agents": result.get("summary", {}).get("total_agents"),
                "debate_rounds": result.get("summary", {}).get("debate_rounds", 0),
                "vote_distribution": result.get("summary", {}).get("final_vote_distribution"),
            },
        }

    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming A2A message (legacy format).

        Args:
            message: A2A message dictionary

        Returns:
            A2A response dictionary
        """
        try:
            # Handle legacy A2A message format
            if "protocol" in message and message.get("protocol") == "a2a/1.0":
                # Legacy format - convert to new format
                # Extract content and parameters
                content = message.get("content", "")
                params = message.get("parameters", {})

                # Process using process_request for simplicity
                response = self.process_request(content, parameters=params)

                # Add A2A protocol fields
                response["protocol"] = "a2a/1.0"
                if "metadata" in response:
                    response["metadata"]["consensus_achieved"] = response["metadata"].get("consensus_reached", False)

                return response

            else:
                # Try to parse as new A2AMessage format
                a2a_msg = A2AMessage(**message)

                # Extract parameters
                params = a2a_msg.parameters or a2a_msg.metadata or {}

                # Process using process_request
                response = self.process_request(a2a_msg.content, parameters=params)

                # Add A2A protocol fields
                response["protocol"] = "a2a/1.0"
                if "metadata" in response:
                    response["metadata"]["consensus_achieved"] = response["metadata"].get("consensus_reached", False)

                return response

        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            return {
                "status": "error",
                "error": str(e),
                "content": "",
                "protocol": "a2a/1.0",
            }

    def process_request(
        self,
        content: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a request in A2A format (synchronous wrapper).

        Args:
            content: The question or task
            parameters: Optional parameters for the request
            context: Optional context information

        Returns:
            A2A response dictionary
        """
        try:
            # Extract parameters and merge with existing ones
            params = parameters or {}
            models = params.get("models", self.models)
            algorithm = params.get("algorithm", self.algorithm)
            consensus_threshold = params.get("consensus_threshold", self.consensus_threshold)
            max_debate_rounds = params.get("max_debate_rounds", self.max_debate_rounds)

            # Create configuration with display disabled for A2A usage
            if (
                params.get("models")
                or params.get("algorithm")
                or params.get("consensus_threshold")
                or params.get("max_debate_rounds")
            ):
                config = create_config_from_models(
                    models=models,
                    orchestrator_config={
                        "algorithm": algorithm,
                        "consensus_threshold": consensus_threshold,
                        "max_debate_rounds": max_debate_rounds,
                    },
                )
            else:
                config = self.config or create_config_from_models(
                    models=self.models,
                    orchestrator_config={
                        "algorithm": self.algorithm,
                        "consensus_threshold": self.consensus_threshold,
                        "max_debate_rounds": self.max_debate_rounds,
                    },
                )
            # Disable streaming display for A2A agent usage
            config.streaming_display.display_enabled = False

            # Run Canopy
            result = run_mass_with_config(content, config)

            # Return response in expected format
            return {
                "status": "success",
                "content": result["answer"],
                "metadata": {
                    "consensus_reached": result.get("consensus_reached", False),
                    "confidence": result.get("confidence", 0.0),
                    "representative_agent": result.get("representative_agent_id"),
                    "debate_rounds": result.get("summary", {}).get("debate_rounds", 0),
                    "session_duration": result.get("session_duration", 0.0),
                },
            }

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "content": "",
            }

    def get_capabilities(self) -> List[Capability]:
        """Return capability information as a list."""
        return [
            Capability(
                name="multi-agent-consensus",
                description="Achieve consensus through multiple AI agents",
                version="1.0.0",
                parameters={
                    "models": {
                        "type": "array",
                        "description": "List of AI models to use",
                        "required": False,
                        "default": [
                            "gpt-4.1",
                            "claude-opus-4",
                            "gemini-2.5-pro",
                            "grok-4",
                        ],
                    },
                    "consensus_threshold": {
                        "type": "number",
                        "description": "Threshold for reaching consensus",
                        "min": 0.0,
                        "max": 1.0,
                        "default": 0.66,
                    },
                    "max_debate_rounds": {
                        "type": "integer",
                        "description": "Maximum number of debate rounds",
                        "min": 1,
                        "default": 3,
                    },
                },
            ),
            Capability(
                name="tree-based-exploration",
                description="Explore solution space using tree-based algorithms",
                version="1.0.0",
            ),
            Capability(
                name="parallel-processing",
                description="Process queries in parallel across agents",
                version="1.0.0",
            ),
            Capability(
                name="algorithm-selection",
                description="Select from multiple consensus algorithms",
                version="1.0.0",
                parameters={
                    "algorithm": {
                        "type": "string",
                        "description": "Consensus algorithm to use",
                        "enum": ["massgen", "treequest"],
                        "default": "massgen",
                    }
                },
            ),
            Capability(
                name="model-agnostic",
                description="Support for multiple AI model providers",
                version="1.0.0",
            ),
            Capability(
                name="streaming-responses",
                description="Stream responses as they are generated",
                version="1.0.0",
            ),
        ]


# Example usage and A2A endpoint handlers
def create_a2a_handlers(config=None):
    """Create handlers for A2A protocol endpoints.

    Args:
        config: Optional MassConfig to use for the agent

    Returns:
        Dictionary of handler functions
    """
    agent = CanopyA2AAgent(config=config) if config else CanopyA2AAgent()

    def handle_agent_card_request():
        """Handle GET /agent request for agent card."""
        card = agent.get_agent_card()
        return card.to_dict() if hasattr(card, "to_dict") else card

    def handle_capabilities_request():
        """Handle GET /capabilities request."""
        capabilities = agent.get_capabilities()
        return [cap.to_dict() for cap in capabilities]

    def handle_message(message: Dict[str, Any]):
        """Handle POST /message request.

        This handles both dictionary messages and structured A2A messages.
        """
        # Handle dictionary input by converting to A2AMessage if needed
        if isinstance(message, dict):
            # Check if it's already an A2A message format
            if "protocol" in message and message.get("protocol") == "a2a/1.0":
                # Legacy A2A message format
                return agent.handle_a2a_message(message)
            else:
                # Simple message format (from tests)
                import uuid
                from datetime import datetime

                # Convert simple message to A2AMessage
                a2a_msg = A2AMessage(
                    id=message.get("id", str(uuid.uuid4())),
                    type=message.get("type", "query"),
                    content=message.get("content", ""),
                    sender_id=message.get("sender_id", "external"),
                    timestamp=message.get("timestamp", datetime.now(timezone.utc).isoformat()),
                    metadata=message.get("parameters", message.get("metadata", {})),
                )

                # Handle synchronously (for compatibility with tests)
                try:
                    if a2a_msg.type == "query":
                        return agent.process_request(a2a_msg.content, parameters=a2a_msg.metadata)
                    else:
                        # Use async handler but run it synchronously
                        import asyncio

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            response = loop.run_until_complete(agent.handle_message(a2a_msg))
                            return response.to_dict()
                        finally:
                            loop.close()
                except Exception as e:
                    return {
                        "status": "error",
                        "error": str(e),
                        "content": "",
                    }

        # If it's already an A2AMessage object, handle it
        return agent.handle_a2a_message(message)

    return {
        "agent_card": handle_agent_card_request,
        "capabilities": handle_capabilities_request,
        "message": handle_message,
    }


if __name__ == "__main__":
    # Example usage with latest 2025 models
    agent = CanopyA2AAgent(models=["gpt-4.1", "claude-opus-4", "gemini-2.5-pro", "grok-4"])

    # Get agent card
    print("Agent Card:")
    card = agent.get_agent_card()
    print(json.dumps(card.to_dict(), indent=2))

    # Process a request
    response = agent.process_request(
        "What are the key differences between supervised and unsupervised learning?",
        parameters={
            "models": ["gpt-4.1", "claude-opus-4", "gemini-2.5-pro", "grok-4"],
            "algorithm": "treequest",
        },
    )

    print("\nResponse:")
    print(json.dumps(response, indent=2))
