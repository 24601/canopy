"""
OpenAI-compatible API server for MassGen inference.

This module provides both completions and chat endpoints compatible with OpenAI's API format.
Supports dynamic configuration and algorithm selection per request.
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .config import load_config_from_yaml
from .main import run_mass_with_config
from .types import AgentConfig, MassConfig, ModelConfig

# Import Canopy A2A components
try:
    from canopy.a2a_agent import CanopyA2AAgent, create_a2a_handlers
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Canopy API Server",
    description="OpenAI-compatible and A2A protocol API for Canopy multi-agent consensus system",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models following OpenAI API spec
class ChatMessage(BaseModel):
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")
    name: Optional[str] = Field(None, description="Optional name of the sender")


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="Sampling temperature")
    top_p: Optional[float] = Field(1.0, ge=0, le=1, description="Nucleus sampling parameter")
    n: Optional[int] = Field(1, ge=1, description="Number of completions to generate")
    stream: Optional[bool] = Field(False, description="Whether to stream responses")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2)
    logit_bias: Optional[Dict[str, float]] = Field(None)
    user: Optional[str] = Field(None, description="Unique identifier for end-user")

    # MassGen-specific extensions
    algorithm: Optional[str] = Field("massgen", description="Algorithm to use (massgen or treequest)")
    agent_models: Optional[List[str]] = Field(None, description="List of models for agents")
    consensus_threshold: Optional[float] = Field(0.51, description="Consensus threshold")
    max_debate_rounds: Optional[int] = Field(3, description="Maximum debate rounds")
    config_path: Optional[str] = Field(None, description="Path to config file to use")


class CompletionRequest(BaseModel):
    model: str = Field(..., description="Model to use for completion")
    prompt: Union[str, List[str]] = Field(..., description="Prompt(s) to complete")
    suffix: Optional[str] = Field(None, description="Suffix to append after completion")
    max_tokens: Optional[int] = Field(16, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(1.0, ge=0, le=2)
    top_p: Optional[float] = Field(1.0, ge=0, le=1)
    n: Optional[int] = Field(1, ge=1)
    stream: Optional[bool] = Field(False)
    logprobs: Optional[int] = Field(None)
    echo: Optional[bool] = Field(False)
    stop: Optional[Union[str, List[str]]] = Field(None)
    presence_penalty: Optional[float] = Field(0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(0, ge=-2, le=2)
    best_of: Optional[int] = Field(1, ge=1)
    logit_bias: Optional[Dict[str, float]] = Field(None)
    user: Optional[str] = Field(None)

    # MassGen-specific extensions
    algorithm: Optional[str] = Field("massgen")
    agent_models: Optional[List[str]] = Field(None)
    consensus_threshold: Optional[float] = Field(0.51)
    max_debate_rounds: Optional[int] = Field(3)
    config_path: Optional[str] = Field(None)


class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Dict[str, int]

    # MassGen-specific metadata
    massgen_metadata: Optional[Dict[str, Any]] = None


class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[Dict] = None
    finish_reason: Optional[str] = None


class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: Dict[str, int]

    # MassGen-specific metadata
    massgen_metadata: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


def create_massgen_config(
    request: Union[ChatCompletionRequest, CompletionRequest], default_config_path: Optional[str] = None
) -> MassConfig:
    """Create MassGen configuration from request parameters."""

    # If config path is specified, load it as base
    if request.config_path:
        config = load_config_from_yaml(request.config_path)
    elif default_config_path:
        config = load_config_from_yaml(default_config_path)
    else:
        # Create minimal config
        config = MassConfig()

    # Override with request parameters
    config.orchestrator.algorithm = request.algorithm
    config.orchestrator.consensus_threshold = request.consensus_threshold
    config.orchestrator.max_debate_rounds = request.max_debate_rounds

    # Handle agent models
    if request.agent_models:
        # Clear existing agents and create new ones
        config.agents = []
        for i, model in enumerate(request.agent_models):
            agent_config = AgentConfig(
                agent_id=i,  # Use integer for agent_id
                agent_type="openai",  # Default, will be determined by model name
                model_config=ModelConfig(
                    model=model,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    max_tokens=request.max_tokens if hasattr(request, "max_tokens") else None,
                ),
            )

            # Determine agent type based on model name
            if "gpt" in model.lower() or "o1" in model.lower():
                agent_config.agent_type = "openai"
            elif "claude" in model.lower():
                agent_config.agent_type = "anthropic"
            elif "gemini" in model.lower():
                agent_config.agent_type = "gemini"
            elif "grok" in model.lower():
                agent_config.agent_type = "xai"
            else:
                # Assume OpenRouter for unknown models
                agent_config.agent_type = "openrouter"

            config.agents.append(agent_config)

    # If only one model specified in 'model' field, use it
    elif not config.agents:
        agent_config = AgentConfig(
            agent_id=0,  # Use integer for agent_id
            agent_type="openai",
            model_config=ModelConfig(
                model=request.model,
                temperature=request.temperature,
                top_p=request.top_p,
                max_tokens=request.max_tokens if hasattr(request, "max_tokens") else None,
            ),
        )
        config.agents = [agent_config]

    return config


def extract_question_from_messages(messages: List[ChatMessage]) -> str:
    """Extract the question from chat messages."""
    # Get the last user message as the question
    for message in reversed(messages):
        if message.role == "user":
            return message.content

    # If no user message, concatenate all messages
    return "\n".join([f"{msg.role}: {msg.content}" for msg in messages])


def estimate_token_count(text: str) -> int:
    """Rough estimation of token count."""
    # Approximate: 1 token ≈ 4 characters
    return len(text) // 4


@app.get("/v1/models")
async def list_models() -> Dict[str, Any]:
    """List available models."""
    # List common models that can be used with Canopy
    models = [
        {
            "id": "canopy-gpt4",
            "object": "model",
            "created": 1686935002,
            "owned_by": "canopy",
            "permission": [],
            "root": "canopy-gpt4",
            "parent": None,
        },
        {
            "id": "canopy-claude3",
            "object": "model",
            "created": 1686935002,
            "owned_by": "canopy",
            "permission": [],
            "root": "canopy-claude3",
            "parent": None,
        },
        {
            "id": "canopy-gemini",
            "object": "model",
            "created": 1686935002,
            "owned_by": "canopy",
            "permission": [],
            "root": "canopy-gemini",
            "parent": None,
        },
        {
            "id": "canopy-multi",
            "object": "model",
            "created": 1686935002,
            "owned_by": "canopy",
            "permission": [],
            "root": "canopy-multi",
            "parent": None,
        },
    ]

    return {"object": "list", "data": models}


@app.post("/v1/chat/completions", response_model=Union[ChatCompletionResponse, ErrorResponse])
async def create_chat_completion(request: ChatCompletionRequest) -> Union[ChatCompletionResponse, ErrorResponse]:
    """Create a chat completion using MassGen."""
    try:
        # Extract question from messages
        question = extract_question_from_messages(request.messages)

        # Create MassGen configuration
        config = create_massgen_config(request)

        # Handle streaming
        if request.stream:
            return StreamingResponse(stream_chat_completion(request, question, config), media_type="text/event-stream")

        # Run MassGen
        start_time = time.time()
        result = await asyncio.to_thread(run_mass_with_config, question, config)

        # Create response
        response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

        # Extract answer
        answer = result.get("answer", "No answer generated")

        # Calculate token usage (rough estimation)
        prompt_tokens = sum(estimate_token_count(msg.content) for msg in request.messages)
        completion_tokens = estimate_token_count(answer)

        response = ChatCompletionResponse(
            id=response_id,
            created=int(time.time()),
            model=request.model,
            choices=[ChatChoice(index=0, message=ChatMessage(role="assistant", content=answer), finish_reason="stop")],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            massgen_metadata={
                "consensus_reached": result.get("consensus_reached", False),
                "representative_agent": result.get("representative_agent_id"),
                "debate_rounds": result.get("summary", {}).get("debate_rounds", 0),
                "total_agents": result.get("summary", {}).get("total_agents", 1),
                "algorithm": config.orchestrator.algorithm,
                "duration": time.time() - start_time,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        return ErrorResponse(error={"message": str(e), "type": "internal_server_error", "code": 500})


@app.post("/v1/completions", response_model=Union[CompletionResponse, ErrorResponse])
async def create_completion(request: CompletionRequest) -> Union[CompletionResponse, ErrorResponse]:
    """Create a text completion using MassGen."""
    try:
        # Handle prompt list
        if isinstance(request.prompt, list):
            prompt = request.prompt[0] if request.prompt else ""
        else:
            prompt = request.prompt

        # Create MassGen configuration
        config = create_massgen_config(request)

        # Handle streaming
        if request.stream:
            return StreamingResponse(stream_completion(request, prompt, config), media_type="text/event-stream")

        # Run MassGen
        start_time = time.time()
        result = await asyncio.to_thread(run_mass_with_config, prompt, config)

        # Create response
        response_id = f"cmpl-{uuid.uuid4().hex[:8]}"

        # Extract answer
        answer = result.get("answer", "No answer generated")

        # Add suffix if provided
        if request.suffix:
            answer += request.suffix

        # Add echo if requested
        if request.echo:
            answer = prompt + answer

        # Calculate token usage
        prompt_tokens = estimate_token_count(prompt)
        completion_tokens = estimate_token_count(answer)

        response = CompletionResponse(
            id=response_id,
            created=int(time.time()),
            model=request.model,
            choices=[CompletionChoice(text=answer, index=0, finish_reason="stop")],
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            massgen_metadata={
                "consensus_reached": result.get("consensus_reached", False),
                "representative_agent": result.get("representative_agent_id"),
                "debate_rounds": result.get("summary", {}).get("debate_rounds", 0),
                "total_agents": result.get("summary", {}).get("total_agents", 1),
                "algorithm": config.orchestrator.algorithm,
                "duration": time.time() - start_time,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Error in completion: {e}")
        return ErrorResponse(error={"message": str(e), "type": "internal_server_error", "code": 500})


async def stream_chat_completion(
    request: ChatCompletionRequest, question: str, config: MassConfig
) -> AsyncIterator[str]:
    """Stream chat completion responses."""
    response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    # Collect streamed content
    streamed_content = []

    def stream_callback(agent_id: str, content: str):
        """Callback to capture streaming content."""
        streamed_content.append(content)

    # Enable streaming in config
    config.streaming_display.display_enabled = True
    config.streaming_display.stream_callback = stream_callback

    try:
        # Run MassGen in thread
        await asyncio.to_thread(run_mass_with_config, question, config)

        # Stream the collected content
        for i, chunk in enumerate(streamed_content):
            data = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.01)  # Small delay for streaming effect

        # Send final chunk
        data = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(data)}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_data = {"error": {"message": str(e), "type": "internal_server_error", "code": 500}}
        yield f"data: {json.dumps(error_data)}\n\n"


async def stream_completion(request: CompletionRequest, prompt: str, config: MassConfig) -> AsyncIterator[str]:
    """Stream completion responses."""
    response_id = f"cmpl-{uuid.uuid4().hex[:8]}"

    # Collect streamed content
    streamed_content = []

    def stream_callback(agent_id: str, content: str):
        """Callback to capture streaming content."""
        streamed_content.append(content)

    # Enable streaming in config
    config.streaming_display.display_enabled = True
    config.streaming_display.stream_callback = stream_callback

    try:
        # Run MassGen in thread
        await asyncio.to_thread(run_mass_with_config, prompt, config)

        # Add echo if requested
        if request.echo:
            yield f"data: {json.dumps({'id': response_id, 'object': 'text_completion', 'created': int(time.time()), 'model': request.model, 'choices': [{'text': prompt, 'index': 0, 'finish_reason': None}]})}\n\n"

        # Stream the collected content
        for chunk in streamed_content:
            data = {
                "id": response_id,
                "object": "text_completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{"text": chunk, "index": 0, "finish_reason": None}],
            }
            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.01)

        # Add suffix if provided
        if request.suffix:
            data = {
                "id": response_id,
                "object": "text_completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{"text": request.suffix, "index": 0, "finish_reason": None}],
            }
            yield f"data: {json.dumps(data)}\n\n"

        # Send final chunk
        data = {
            "id": response_id,
            "object": "text_completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{"text": "", "index": 0, "finish_reason": "stop"}],
        }
        yield f"data: {json.dumps(data)}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_data = {"error": {"message": str(e), "type": "internal_server_error", "code": 500}}
        yield f"data: {json.dumps(error_data)}\n\n"


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "canopy-api", "version": "1.0.0"}


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    endpoints = {
        "service": "Canopy API Server",
        "description": "Multi-agent consensus system with OpenAI and A2A protocol support",
        "endpoints": {
            "openai": {
                "chat": "/v1/chat/completions",
                "completions": "/v1/completions",
                "models": "/v1/models",
            },
            "health": "/health",
            "documentation": "/docs",
            "openapi": "/openapi.json"
        },
        "credits": "Built on MassGen by AG2 team"
    }
    
    if A2A_AVAILABLE:
        endpoints["endpoints"]["a2a"] = {
            "agent_card": "/agent",
            "capabilities": "/capabilities",
            "message": "/message"
        }
    
    return endpoints


# A2A Protocol Endpoints
if A2A_AVAILABLE:
    # Initialize A2A handlers
    a2a_handlers = create_a2a_handlers()
    
    @app.get("/agent")
    async def get_agent_card() -> Dict[str, Any]:
        """Get A2A agent card."""
        return a2a_handlers["agent_card"]()
    
    @app.get("/capabilities")
    async def get_capabilities() -> Dict[str, Any]:
        """Get detailed agent capabilities."""
        return a2a_handlers["capabilities"]()
    
    @app.post("/message")
    async def handle_a2a_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle A2A protocol message."""
        return a2a_handlers["message"](message)


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
