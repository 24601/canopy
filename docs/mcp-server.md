# Canopy MCP Server

The Canopy MCP (Model Context Protocol) server allows integration with MCP-compatible tools like Claude Desktop, enabling seamless access to Canopy's multi-agent capabilities.

## Installation

The MCP server is included with the Canopy installation. Ensure you have installed Canopy:

```bash
pip install -e .
```

## Configuration

### For Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "canopy": {
      "command": "python",
      "args": ["-m", "canopy.mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/canopy",
        "OPENAI_API_KEY": "your-key",
        "ANTHROPIC_API_KEY": "your-key",
        "GEMINI_API_KEY": "your-key"
      }
    }
  }
}
```

### Standalone Usage

You can also run the MCP server standalone:

```bash
python -m canopy.mcp_server
```

## Available Tools

### canopy_query

Query Canopy with multiple AI agents for consensus-based answers.

**Parameters:**
- `question` (required): The question or task to solve
- `models`: List of AI models to use (default: ["gpt-4", "claude-3"])
- `algorithm`: Algorithm to use - "massgen" or "treequest" (default: "massgen")
- `consensus_threshold`: Consensus threshold 0.0-1.0 (default: 0.66)
- `max_debate_rounds`: Maximum debate rounds 1-10 (default: 3)
- `include_metadata`: Include detailed metadata in response (default: false)

**Example:**
```
Use canopy_query to explain quantum computing with models gpt-4 and claude-3
```

### canopy_query_config

Query Canopy using a pre-defined configuration file.

**Parameters:**
- `question` (required): The question or task to solve
- `config_path` (required): Path to YAML configuration file
- `include_metadata`: Include detailed metadata in response (default: false)

**Example:**
```
Use canopy_query_config with config examples/fast_config.yaml to analyze market trends
```

### canopy_analyze

Analyze a problem with different algorithm profiles and comparisons.

**Parameters:**
- `question` (required): The question or problem to analyze
- `analysis_type`: Type of analysis - "compare_algorithms", "compare_models", or "sensitivity_analysis"
- `models`: Models to use in analysis (default: ["gpt-4", "claude-3"])

**Example:**
```
Use canopy_analyze to compare algorithms for solving a math problem
```

## Available Resources

### canopy://config/examples

Pre-configured examples for different use cases:
- `fast`: Lightweight models for quick responses
- `balanced`: Balanced configuration for general use
- `thorough`: Advanced models for detailed analysis

### canopy://algorithms

Information about available consensus algorithms:
- `massgen`: Original parallel processing with democratic voting
- `treequest`: Tree-based exploration inspired by MCTS

### canopy://models

List of supported AI models organized by provider:
- OpenAI: gpt-4, gpt-3.5-turbo, o1-preview
- Anthropic: claude-3-opus, claude-3-sonnet, claude-3-haiku
- Google: gemini-ultra, gemini-pro, gemini-flash
- xAI: grok-3, grok-2

## Usage Examples

### Basic Query

```
Can you use canopy to analyze the environmental impact of electric vehicles?
Use 3 different models for a comprehensive perspective.
```

### Algorithm Comparison

```
Use canopy_analyze to compare how massgen and treequest algorithms
handle this step-by-step problem: "How do you build a treehouse?"
```

### Using Configuration

```
Use canopy_query_config with the thorough configuration to research
the latest advances in quantum computing.
```

## Troubleshooting

### MCP Server Not Found

Ensure Canopy is properly installed and the Python path includes the Canopy directory:

```bash
export PYTHONPATH=/path/to/canopy:$PYTHONPATH
```

### API Key Errors

Make sure all required API keys are set in your environment or Claude Desktop config:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GEMINI_API_KEY
- XAI_API_KEY
- OPENROUTER_API_KEY (optional)

### Connection Issues

Check that the MCP server is running:

```bash
python -m canopy.mcp_server
```

You should see output indicating the server is ready to accept connections.
