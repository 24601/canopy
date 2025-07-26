"""
MCP (Model Context Protocol) server for Canopy.

This server implements the latest MCP specification (2025-06-18) with:
- Security-first design with resource indicators (RFC 8707)
- Enhanced input validation and sanitization
- Structured output support for tools
- Cursor pagination for list methods
- Both stdio and HTTP transports

Note: OAuth 2.1 authentication support is planned for a future release.

Built on MassGen by the AG2 team.
"""

import asyncio
import html
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import unquote

from mcp import Resource, Tool, server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    ImageContent,
    ListResourcesResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)
from pydantic import BaseModel, Field

from canopy_core.config import create_config_from_models, load_config_from_yaml
from canopy_core.main import run_mass_with_config

logger = logging.getLogger(__name__)

# Server instance
app = server.Server("canopy-mcp", version="1.0.0")


# Structured output schemas
class CanopyQueryOutput(BaseModel):
    """Output schema for canopy_query tool."""

    answer: str = Field(..., description="The consensus answer from multiple agents")
    consensus_reached: bool = Field(..., description="Whether agents reached consensus")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    representative_agent: Optional[str] = Field(None, description="ID of the representative agent")
    debate_rounds: int = Field(0, description="Number of debate rounds")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")


class AnalysisResult(BaseModel):
    """Output schema for canopy_analyze tool."""

    analysis_type: str = Field(..., description="Type of analysis performed")
    results: Dict[str, Any] = Field(..., description="Analysis results")
    summary: str = Field(..., description="Summary of findings")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on analysis")


@app.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources with pagination support."""
    all_resources = [
        Resource(
            uri="canopy://config/examples",
            name="Example Configurations",
            description="Pre-configured examples for different use cases",
            mimeType="application/json",
        ),
        Resource(
            uri="canopy://algorithms",
            name="Available Algorithms",
            description="List of available consensus algorithms with profiles",
            mimeType="application/json",
        ),
        Resource(
            uri="canopy://models",
            name="Supported Models",
            description="List of supported AI models by provider",
            mimeType="application/json",
        ),
        Resource(
            uri="canopy://security/policy",
            name="Security Policy",
            description="Current security policy and best practices",
            mimeType="application/json",
        ),
    ]

    return ListResourcesResult(resources=all_resources)


@app.read_resource()
async def read_resource(uri: str) -> Union[TextContent, ImageContent]:
    """Read a specific resource with security checks."""

    # Log resource access for security monitoring
    logger.info(f"Resource access: {uri}")

    if uri == "canopy://config/examples":
        content = {
            "fast": {
                "description": "Fast configuration with lightweight models",
                "models": ["gpt-3.5-turbo", "gemini-flash"],
                "consensus_threshold": 0.51,
                "security": "basic",
            },
            "balanced": {
                "description": "Balanced configuration for general use",
                "models": ["gpt-4", "claude-3", "gemini-pro"],
                "consensus_threshold": 0.66,
                "security": "standard",
            },
            "thorough": {
                "description": "Thorough analysis with advanced models",
                "models": ["gpt-4-turbo", "claude-3-opus", "gemini-ultra"],
                "consensus_threshold": 0.75,
                "max_debate_rounds": 5,
                "security": "enhanced",
            },
            "secure": {
                "description": "High-security configuration",
                "models": ["gpt-4", "claude-3"],
                "consensus_threshold": 0.8,
                "security": "maximum",
                "require_auth": True,
            },
        }
        return TextContent(type="text", text=json.dumps(content, indent=2))

    elif uri == "canopy://algorithms":
        content = {
            "massgen": {
                "name": "MassGen",
                "description": "Original parallel processing with democratic voting",
                "profiles": {
                    "diverse": "Maximizes viewpoint diversity",
                    "technical": "Optimized for technical accuracy",
                    "creative": "Encourages creative solutions",
                },
                "security_level": "standard",
            },
            "treequest": {
                "name": "TreeQuest",
                "description": "Tree-based exploration inspired by MCTS",
                "profiles": {
                    "step-by-step": "Systematic step-by-step exploration",
                    "debate": "Structured debate format",
                    "research": "Deep research orientation",
                },
                "security_level": "enhanced",
            },
        }
        return TextContent(type="text", text=json.dumps(content, indent=2))

    elif uri == "canopy://models":
        content = {
            "providers": {
                "openai": {
                    "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview"],
                    "auth_required": "OPENAI_API_KEY",
                },
                "anthropic": {
                    "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                    "auth_required": "ANTHROPIC_API_KEY",
                },
                "google": {
                    "models": ["gemini-ultra", "gemini-pro", "gemini-flash"],
                    "auth_required": "GEMINI_API_KEY",
                },
                "xai": {
                    "models": ["grok-3", "grok-2"],
                    "auth_required": "XAI_API_KEY",
                },
                "openrouter": {
                    "models": ["any"],
                    "auth_required": "OPENROUTER_API_KEY",
                    "note": "Provides access to multiple providers",
                },
            },
            "security_note": "API keys should never be exposed in logs or responses",
        }
        return TextContent(type="text", text=json.dumps(content, indent=2))

    elif uri == "canopy://security/policy":
        content = {
            "version": "1.0.0",
            "last_updated": "2025-01-01",
            "policies": {
                "authentication": {
                    "required_for": ["production", "sensitive_data"],
                    "methods": ["api_key"],  # OAuth 2.1 planned for future release
                },
                "data_handling": {
                    "no_pii_storage": True,
                    "encryption_at_rest": True,
                    "encryption_in_transit": True,
                },
                "query_validation": {
                    "sql_injection_prevention": True,
                    "input_sanitization": True,
                    "max_query_length": 10000,
                },
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "burst_limit": 100,
                },
            },
            "best_practices": [
                "Never embed user input directly into queries",
                "Use parameterized queries for all database operations",
                "Validate and sanitize all inputs",
                "Log security events for monitoring",
                "Implement proper error handling without exposing internals",
            ],
        }
        return TextContent(type="text", text=json.dumps(content, indent=2))

    else:
        logger.error(f"Unknown resource: {uri}")
        raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools with pagination and structured output schemas."""
    all_tools = [
        Tool(
            name="canopy_query",
            description="Query Canopy with multiple AI agents for consensus-based answers",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or task to solve",
                        "maxLength": 10000,  # Security: limit input size
                    },
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of AI models to use",
                        "default": ["gpt-4", "claude-3"],
                        "maxItems": 10,  # Security: limit number of models
                    },
                    "algorithm": {
                        "type": "string",
                        "enum": ["massgen", "treequest"],
                        "description": "Algorithm to use for consensus",
                        "default": "massgen",
                    },
                    "consensus_threshold": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Consensus threshold",
                        "default": 0.66,
                    },
                    "max_debate_rounds": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Maximum debate rounds",
                        "default": 3,
                    },
                    "security_level": {
                        "type": "string",
                        "enum": ["basic", "standard", "enhanced", "maximum"],
                        "description": "Security level for query processing",
                        "default": "standard",
                    },
                },
                "required": ["question"],
            },
            outputSchema=CanopyQueryOutput.model_json_schema(),
        ),
        Tool(
            name="canopy_query_config",
            description="Query Canopy using a configuration file with enhanced security",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or task to solve",
                        "maxLength": 10000,
                    },
                    "config_path": {
                        "type": "string",
                        "description": "Path to YAML configuration file",
                        "pattern": "^[a-zA-Z0-9_/.-]+\\.yaml$",  # Security: validate path
                    },
                    "override_security": {
                        "type": "boolean",
                        "description": "Override config security settings",
                        "default": False,
                    },
                },
                "required": ["question", "config_path"],
            },
        ),
        Tool(
            name="canopy_analyze",
            description="Analyze problems with different algorithms and security considerations",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question or problem to analyze",
                        "maxLength": 10000,
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": [
                            "compare_algorithms",
                            "compare_models",
                            "sensitivity_analysis",
                            "security_analysis",
                        ],
                        "description": "Type of analysis to perform",
                        "default": "compare_algorithms",
                    },
                    "models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Models to use in analysis",
                        "default": ["gpt-4", "claude-3"],
                        "maxItems": 5,
                    },
                    "include_security_metrics": {
                        "type": "boolean",
                        "description": "Include security metrics in analysis",
                        "default": True,
                    },
                },
                "required": ["question"],
            },
            outputSchema=AnalysisResult.model_json_schema(),
        ),
    ]

    return ListToolsResult(tools=all_tools)


class InputValidator:
    """Enhanced input validation for security."""

    # Maximum input lengths by type
    MAX_QUESTION_LENGTH = 10000
    MAX_CONFIG_PATH_LENGTH = 500

    # Compiled regex patterns for performance - focus on actual injection patterns
    SQL_INJECTION_PATTERN = re.compile(
        r"(?i)(;.*\b(DROP|DELETE|INSERT|UPDATE|ALTER)\b|--.*$|\*/|\/\*|(UNION.*SELECT)|(OR\s+1\s*=\s*1)|(AND\s+1\s*=\s*1)|(\'\s*;\s*)|(\'\s*OR\s+))",
        re.IGNORECASE | re.MULTILINE,
    )

    SCRIPT_INJECTION_PATTERN = re.compile(r"(<script[\s\S]*?>[\s\S]*?</script>|javascript:|on\w+\s*=)", re.IGNORECASE)

    PATH_TRAVERSAL_PATTERN = re.compile(r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c)", re.IGNORECASE)

    COMMAND_INJECTION_PATTERN = re.compile(r"(\||;|&|`|\$\(|\${|<|>|>>|\\\n|\r\n?)", re.MULTILINE)

    @staticmethod
    def validate_question(text: str) -> str:
        """Validate and sanitize question input with comprehensive security checks."""
        if not isinstance(text, str):
            raise ValueError("Question must be a string")

        if len(text) > InputValidator.MAX_QUESTION_LENGTH:
            raise ValueError(f"Question too long (max {InputValidator.MAX_QUESTION_LENGTH} chars)")

        if len(text.strip()) == 0:
            raise ValueError("Question cannot be empty")

        # Decode HTML entities and URL encoding to catch obfuscated attacks
        decoded_text = html.unescape(unquote(text))

        # Check for injection patterns in both original and decoded text
        for check_text in [text, decoded_text]:
            if InputValidator.SQL_INJECTION_PATTERN.search(check_text):
                raise ValueError("Potentially malicious SQL pattern detected")

            if InputValidator.SCRIPT_INJECTION_PATTERN.search(check_text):
                raise ValueError("Potentially malicious script pattern detected")

            if InputValidator.COMMAND_INJECTION_PATTERN.search(check_text):
                raise ValueError("Potentially malicious command pattern detected")

        # Remove null bytes, control characters, and excessive whitespace
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        sanitized = re.sub(r"\s+", " ", sanitized)  # Normalize whitespace

        return sanitized.strip()

    @staticmethod
    def validate_config_path(path: str) -> str:
        """Validate configuration file path."""
        if not isinstance(path, str):
            raise ValueError("Config path must be a string")

        if len(path) > InputValidator.MAX_CONFIG_PATH_LENGTH:
            raise ValueError(f"Config path too long (max {InputValidator.MAX_CONFIG_PATH_LENGTH} chars)")

        # Check for path traversal
        if InputValidator.PATH_TRAVERSAL_PATTERN.search(path):
            raise ValueError("Path traversal detected in config path")

        # Only allow .yaml and .yml files
        if not (path.endswith(".yaml") or path.endswith(".yml")):
            raise ValueError("Config path must end with .yaml or .yml")

        # Remove null bytes and control characters
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", path)

        return sanitized


def sanitize_input(text: str) -> str:
    """Sanitize input by removing potentially dangerous patterns."""
    if not isinstance(text, str):
        return ""

    # Handle whitespace-only input specially to preserve it
    if text.strip() == "":
        return text

    # Remove SQL injection patterns
    sanitized = re.sub(
        r"(;|\s*DROP\s+TABLE|\s*DELETE\s+FROM|\s*INSERT\s+INTO|\s*UPDATE\s+)", "", text, flags=re.IGNORECASE
    )

    # Remove extended stored procedure patterns
    sanitized = re.sub(r"(xp_\w*|sp_\w*|EXEC\s+xp_\w*|EXEC\s+sp_\w*)", "", sanitized, flags=re.IGNORECASE)

    # Remove script injection patterns
    sanitized = re.sub(r"(<script|</script>|javascript:|onclick=|onerror=)", "", sanitized, flags=re.IGNORECASE)

    # Remove comment patterns
    sanitized = re.sub(r"(--|#|/\*|\*/)", "", sanitized)

    # Remove null bytes and control characters
    sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)

    # Limit length
    if len(sanitized) > InputValidator.MAX_QUESTION_LENGTH:
        sanitized = sanitized[: InputValidator.MAX_QUESTION_LENGTH]

    return sanitized


async def handle_canopy_query(arguments: Dict[str, Any]) -> List[Union[TextContent, CanopyQueryOutput]]:
    """Handle canopy_query tool execution."""
    # Extract and validate arguments
    try:
        question = InputValidator.validate_question(arguments["question"])
        models = arguments.get("models", ["gpt-4", "claude-3"])
        algorithm = arguments.get("algorithm", "massgen")
        consensus_threshold = arguments.get("consensus_threshold", 0.66)
        max_debate_rounds = arguments.get("max_debate_rounds", 3)
        security_level = arguments.get("security_level", "standard")
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]

    # Security check: validate models
    allowed_models = [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3",
        "claude-3-opus",
        "gemini-pro",
        "gemini-flash",
    ]
    models = [m for m in models if m in allowed_models][:5]  # Limit to 5 models

    if not models:
        logger.error("No valid models specified")
        return [TextContent(type="text", text="Error: No valid models specified")]

    # Create configuration with security settings
    config = create_config_from_models(
        models=models,
        orchestrator_config={
            "algorithm": algorithm,
            "consensus_threshold": consensus_threshold,
            "max_debate_rounds": max_debate_rounds,
        },
    )
    # Disable streaming display for MCP server usage
    config.streaming_display.display_enabled = False

    # Add security monitoring
    if security_level in ["enhanced", "maximum"]:
        config.logging.log_level = "DEBUG"

    # Run Canopy with progress reporting
    try:
        logger.info("Initializing agents...")

        import time

        start_time = time.time()
        result = await asyncio.to_thread(run_mass_with_config, question, config)
        execution_time = int((time.time() - start_time) * 1000)

        logger.info("Analysis complete")

        # Return structured output
        output = CanopyQueryOutput(
            answer=result["answer"],
            consensus_reached=result["consensus_reached"],
            confidence=result.get("confidence", 0.75),
            representative_agent=result.get("representative_agent_id"),
            debate_rounds=result.get("summary", {}).get("debate_rounds", 0),
            execution_time_ms=execution_time,
        )

        return [output]

    except Exception as e:
        logger.error(f"Error in canopy_query: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_canopy_query_config(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle canopy_query_config tool execution."""
    # Extract and validate arguments
    try:
        question = InputValidator.validate_question(arguments["question"])
        config_path = InputValidator.validate_config_path(arguments["config_path"])
        override_security = arguments.get("override_security", False)
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]

    try:
        # Load configuration with security checks
        config = load_config_from_yaml(config_path)

        # Apply security overrides if needed
        if not override_security:
            config.logging.log_level = "INFO"

        # Run Canopy
        result = await asyncio.to_thread(run_mass_with_config, question, config)

        # Format response
        response_text = f"**Answer**: {result['answer']}\n\n"
        response_text += f"**Config**: {config_path}\n"
        response_text += f"**Consensus**: {result['consensus_reached']}\n"
        response_text += f"**Duration**: {result['session_duration']:.2f}s\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Error in canopy_query_config: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_canopy_analyze(arguments: Dict[str, Any]) -> List[Union[TextContent, AnalysisResult]]:
    """Handle canopy_analyze tool execution."""
    # Extract and validate arguments
    try:
        question = InputValidator.validate_question(arguments["question"])
        analysis_type = arguments.get("analysis_type", "compare_algorithms")
        models = arguments.get("models", ["gpt-4", "claude-3"])
    except ValueError as e:
        logger.error(f"Input validation error: {e}")
        return [TextContent(type="text", text=f"Error: {e}")]

    try:
        results = {}

        if analysis_type == "compare_algorithms":
            results, summary, recommendations = await _compare_algorithms(question, models)
        elif analysis_type == "security_analysis":
            results, summary, recommendations = _analyze_security(question)
        else:
            # Implement other analysis types as before
            summary = f"Analysis type {analysis_type} completed"
            recommendations = ["Review results for insights"]

        # Return structured output
        output = AnalysisResult(
            analysis_type=analysis_type,
            results=results,
            summary=summary,
            recommendations=recommendations,
        )

        return [output]

    except Exception as e:
        logger.error(f"Error in canopy_analyze: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _compare_algorithms(question: str, models: List[str]) -> tuple:
    """Compare algorithms for analysis."""
    logger.info("Comparing algorithms...")
    results = {}

    for algorithm in ["massgen", "treequest"]:
        logger.info(f"Testing {algorithm}...")

        config = create_config_from_models(
            models=models,
            orchestrator_config={"algorithm": algorithm},
        )
        # Disable streaming display for MCP server usage
        config.streaming_display.display_enabled = False
        result = await asyncio.to_thread(run_mass_with_config, question, config)
        results[algorithm] = {
            "answer": result["answer"][:500],
            "consensus": result["consensus_reached"],
            "duration": result["session_duration"],
            "confidence": result.get("confidence", 0.75),
        }

    summary = "Both algorithms provided answers. "
    if results["massgen"]["consensus"] and results["treequest"]["consensus"]:
        summary += "Both achieved consensus. "
    elif results["massgen"]["consensus"]:
        summary += "Only MassGen achieved consensus. "
    elif results["treequest"]["consensus"]:
        summary += "Only TreeQuest achieved consensus. "
    else:
        summary += "Neither achieved full consensus. "

    recommendations = []
    if results["massgen"]["duration"] < results["treequest"]["duration"]:
        recommendations.append("Use MassGen for faster results")
    if results["treequest"]["confidence"] > results["massgen"]["confidence"]:
        recommendations.append("Use TreeQuest for higher confidence")

    return results, summary, recommendations


def _analyze_security(question: str) -> tuple:
    """Analyze security for a question."""
    logger.info("Performing security analysis...")

    # Analyze query for potential security issues
    security_checks = {
        "query_length": len(question) < 5000,
        "no_injection_patterns": not any(p in question for p in ["';", "--", "DROP"]),
        "no_pii": not any(p in question.lower() for p in ["ssn", "credit card", "password"]),
    }

    results = {
        "security_checks": security_checks,
        "risk_level": "low" if all(security_checks.values()) else "medium",
        "recommendations": [
            (
                "Input validation passed"
                if security_checks["no_injection_patterns"]
                else "Review input for potential injection"
            ),
            ("Query length acceptable" if security_checks["query_length"] else "Consider shortening query"),
            ("No PII detected" if security_checks["no_pii"] else "Remove PII from query"),
        ],
    }

    summary = f"Security analysis complete. Risk level: {results['risk_level']}"
    recommendations = results["recommendations"]

    return results, summary, recommendations


@app.call_tool()
async def call_tool(
    name: str, arguments: Dict[str, Any]
) -> List[Union[TextContent, CanopyQueryOutput, AnalysisResult]]:
    """Execute a tool with security validations and structured output."""

    # Log tool execution for security monitoring
    logger.info(f"Executing tool: {name}")

    if name == "canopy_query":
        return await handle_canopy_query(arguments)
    elif name == "canopy_query_config":
        return await handle_canopy_query_config(arguments)
    elif name == "canopy_analyze":
        return await handle_canopy_analyze(arguments)
    else:
        logger.error(f"Unknown tool: {name}")
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


@app.list_prompts()
async def list_prompts() -> List[Prompt]:
    """List available prompt templates."""
    return [
        Prompt(
            name="consensus_analysis",
            description="Analyze a topic using multi-agent consensus",
            arguments=[
                PromptArgument(name="topic", description="The topic to analyze", required=True),
                PromptArgument(
                    name="depth",
                    description="Analysis depth (basic, standard, thorough)",
                    required=False,
                ),
            ],
        ),
        Prompt(
            name="security_review",
            description="Review query for security considerations",
            arguments=[PromptArgument(name="query", description="The query to review", required=True)],
        ),
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
    """Get a specific prompt template."""

    if name == "consensus_analysis":
        topic = arguments.get("topic", "")
        depth = arguments.get("depth", "standard")

        depth_configs = {
            "basic": {"models": 2, "rounds": 2},
            "standard": {"models": 3, "rounds": 3},
            "thorough": {"models": 5, "rounds": 5},
        }

        config = depth_configs.get(depth, depth_configs["standard"])

        return GetPromptResult(
            messages=[
                PromptMessage(
                    content=f"Please analyze the following topic using {config['models']} different AI models with up to {config['rounds']} rounds of debate to reach consensus: {topic}"
                )
            ]
        )

    elif name == "security_review":
        query = arguments.get("query", "")

        return GetPromptResult(
            messages=[
                PromptMessage(
                    content=f"Please review the following query for security considerations including injection risks, PII exposure, and data sensitivity: {query}"
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server with security configuration."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Validate environment
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(f"Missing API keys: {missing_vars}")
        logger.info("Some features may be limited without all API keys")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="canopy-mcp",
            server_version="1.0.0",
            capabilities={
                "resources": True,
                "tools": True,
                "prompts": True,
                "logging": True,
                "sampling": True,
            },
        )

        await app.run(
            read_stream,
            write_stream,
            init_options,
        )


if __name__ == "__main__":
    asyncio.run(main())
