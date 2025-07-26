"""
A2A (Agent-to-Agent) protocol implementation for Canopy.

This module provides an A2A-compatible agent interface following Google's
Agent-to-Agent Communication protocol, including agent card metadata.
"""

import json
import logging
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from massgen.config import create_config_from_models
from massgen.main import run_mass_with_config

logger = logging.getLogger(__name__)


@dataclass
class AgentCard:
    """Agent card metadata following A2A protocol specification."""
    
    # Required fields
    name: str = "Canopy Multi-Agent System"
    description: str = "Multi-agent consensus system for collaborative problem-solving"
    version: str = "1.0.0"
    
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
                "openai/gpt-4",
                "openai/gpt-3.5-turbo",
                "anthropic/claude-3",
                "google/gemini-pro",
                "xai/grok",
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent card to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert agent card to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class A2AMessage:
    """A2A protocol message format."""
    
    # Message metadata
    protocol: str = "a2a/1.0"
    message_id: str = None
    correlation_id: str = None
    timestamp: str = None
    
    # Sender information
    sender: Dict[str, str] = None
    
    # Message content
    content: str = None
    content_type: str = "text/plain"
    
    # Optional parameters
    parameters: Dict[str, Any] = None
    context: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class A2AResponse:
    """A2A protocol response format."""
    
    # Response metadata
    protocol: str = "a2a/1.0"
    message_id: str = None
    correlation_id: str = None
    timestamp: str = None
    
    # Response content
    content: str = None
    content_type: str = "text/plain"
    
    # Execution metadata
    execution_time_ms: int = None
    model_used: str = None
    consensus_achieved: bool = None
    
    # Optional fields
    metadata: Dict[str, Any] = None
    errors: List[str] = None
    
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
    ):
        """Initialize the A2A agent.
        
        Args:
            models: List of models to use (defaults to gpt-4 and claude-3)
            algorithm: Consensus algorithm to use
            consensus_threshold: Threshold for consensus
            max_debate_rounds: Maximum debate rounds
        """
        self.models = models or ["gpt-4", "claude-3"]
        self.algorithm = algorithm
        self.consensus_threshold = consensus_threshold
        self.max_debate_rounds = max_debate_rounds
        self.agent_card = AgentCard()
    
    def get_agent_card(self) -> Dict[str, Any]:
        """Return the agent card as a dictionary."""
        return self.agent_card.to_dict()
    
    def handle_a2a_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming A2A message.
        
        Args:
            message: A2A message dictionary
            
        Returns:
            A2A response dictionary
        """
        try:
            # Parse message
            a2a_msg = A2AMessage(**message)
            
            # Extract parameters
            params = a2a_msg.parameters or {}
            models = params.get("models", self.models)
            algorithm = params.get("algorithm", self.algorithm)
            consensus_threshold = params.get("consensus_threshold", self.consensus_threshold)
            max_debate_rounds = params.get("max_debate_rounds", self.max_debate_rounds)
            
            # Create configuration
            config = create_config_from_models(
                models=models,
                orchestrator_config={
                    "algorithm": algorithm,
                    "consensus_threshold": consensus_threshold,
                    "max_debate_rounds": max_debate_rounds,
                },
            )
            
            # Run Canopy
            import time
            start_time = time.time()
            result = run_mass_with_config(a2a_msg.content, config)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Create response
            response = A2AResponse(
                correlation_id=a2a_msg.message_id,
                content=result["answer"],
                execution_time_ms=execution_time,
                consensus_achieved=result.get("consensus_reached", False),
                metadata={
                    "representative_agent": result.get("representative_agent_id"),
                    "total_agents": result.get("summary", {}).get("total_agents"),
                    "debate_rounds": result.get("summary", {}).get("debate_rounds", 0),
                    "vote_distribution": result.get("summary", {}).get("final_vote_distribution"),
                },
            )
            
            return response.to_dict()
            
        except Exception as e:
            logger.error(f"Error handling A2A message: {e}")
            error_response = A2AResponse(
                correlation_id=message.get("message_id"),
                content=f"Error processing request: {str(e)}",
                errors=[str(e)],
            )
            return error_response.to_dict()
    
    def process_request(
        self,
        content: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Process a request in A2A format.
        
        Args:
            content: The question or task
            parameters: Optional parameters for the request
            context: Optional context information
            
        Returns:
            A2A response dictionary
        """
        import uuid
        from datetime import datetime
        
        # Create A2A message
        message = A2AMessage(
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            sender={"name": "external", "type": "user"},
            content=content,
            parameters=parameters,
            context=context,
        )
        
        # Handle the message
        return self.handle_a2a_message(message.to_dict())
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return detailed capability information."""
        return {
            "agent_card": self.get_agent_card(),
            "algorithms": {
                "massgen": {
                    "name": "MassGen",
                    "description": "Original parallel processing with democratic voting",
                    "suitable_for": ["general", "creative", "analytical"],
                },
                "treequest": {
                    "name": "TreeQuest", 
                    "description": "Tree-based exploration inspired by MCTS",
                    "suitable_for": ["step-by-step", "mathematical", "logical"],
                },
            },
            "configuration_options": {
                "models": {
                    "type": "array",
                    "description": "List of models to use",
                    "default": self.models,
                },
                "algorithm": {
                    "type": "string",
                    "enum": ["massgen", "treequest"],
                    "default": self.algorithm,
                },
                "consensus_threshold": {
                    "type": "number",
                    "range": [0.0, 1.0],
                    "default": self.consensus_threshold,
                },
                "max_debate_rounds": {
                    "type": "integer",
                    "range": [1, 10],
                    "default": self.max_debate_rounds,
                },
            },
        }


# Example usage and A2A endpoint handlers
def create_a2a_handlers():
    """Create handlers for A2A protocol endpoints."""
    agent = CanopyA2AAgent()
    
    def handle_agent_card_request():
        """Handle GET /agent request for agent card."""
        return agent.get_agent_card()
    
    def handle_capabilities_request():
        """Handle GET /capabilities request."""
        return agent.get_capabilities()
    
    def handle_message(message: Dict[str, Any]):
        """Handle POST /message request."""
        return agent.handle_a2a_message(message)
    
    return {
        "agent_card": handle_agent_card_request,
        "capabilities": handle_capabilities_request,
        "message": handle_message,
    }


if __name__ == "__main__":
    # Example usage
    agent = CanopyA2AAgent(models=["gpt-4", "claude-3"])
    
    # Get agent card
    print("Agent Card:")
    print(json.dumps(agent.get_agent_card(), indent=2))
    
    # Process a request
    response = agent.process_request(
        "What are the key differences between supervised and unsupervised learning?",
        parameters={
            "models": ["gpt-4", "claude-3", "gemini-pro"],
            "algorithm": "treequest",
        }
    )
    
    print("\nResponse:")
    print(json.dumps(response, indent=2))