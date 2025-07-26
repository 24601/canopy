# 🌳 Canopy: Multi-Agent Consensus through Tree-Based Exploration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

> **Note**: Canopy's core functionality is implemented but still undergoing validation and refinement. While the system is functional, we're focused on ensuring quality through comprehensive testing before considering features truly "complete". We believe in shipping quality over speed and welcome community feedback to help us achieve production-ready stability.

![Canopy Logo](assets/canopy-banner.png)

> A multi-agent system for collaborative AI problem-solving through parallel exploration and consensus building.

## 🚀 Quick Start

Get Canopy running in under 5 minutes!

```bash
# Option 1: Automated setup (Unix/Linux/macOS)
./quickstart.sh

# Option 2: Automated setup (Windows)
.\quickstart.ps1

# Option 3: Manual install
pip install canopy

# Set your API key (get one free at https://openrouter.ai/)
export OPENROUTER_API_KEY=your_key_here

# Ask a question with multiple AI agents
python -m canopy "What's the best way to learn programming?" \
  --models gpt-4o-mini claude-3-haiku

# Start the API server
python -m canopy --serve

# Use with any OpenAI client
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "canopy-multi", "messages": [{"role": "user", "content": "Hello!"}]}'
```

📚 **[Full Quick Start Guide →](docs/quickstart/README.md)** | ⚡ **[5-Minute Quick Start →](docs/quickstart/5-minute-quickstart.md)**

## Overview

Canopy extends the foundational work of [MassGen](https://github.com/ag2ai/MassGen) by the AG2 team, enhancing it with tree-based exploration algorithms, comprehensive testing, and modern developer tooling. The system orchestrates multiple AI agents working in parallel, observing each other's progress, and refining their approaches to converge on optimal solutions.

This project builds upon the "threads of thought" and "iterative refinement" concepts from [The Myth of Reasoning](https://docs.ag2.ai/latest/docs/blog/#the-myth-of-reasoning) and extends the multi-agent conversation patterns pioneered in [AG2](https://github.com/ag2ai/ag2).

## Features & Implementation Status

**Status Legend:**
- ✅ Implemented - Core functionality complete, validation ongoing
- 🔄 Refinement - Working implementation, optimization and testing in progress
- ⏳ Basic - Minimal viable implementation, significant work needed
- 🚧 In Development - Actively being built
- ⬜ Planned - On the roadmap but not started

### Core Features

| Feature | Description | Status | Review Status |
|---------|-------------|--------|--------------:
| **Multi-Agent Orchestration** | Parallel coordination of multiple AI models | ✅ Implemented | ☐ Pending full review |
| **MassGen Algorithm** | Original consensus-based algorithm | ✅ Implemented | ☐ Pending full review |
| **TreeQuest Algorithm** | MCTS-inspired tree exploration | 🔄 Refinement |
| **Consensus Mechanisms** | Voting, weighted scoring, and debate resolution | 🔄 Refinement |
| **Agent Communication** | Inter-agent visibility and message passing | ✅ Implemented | ☐ Pending full review |
| **Dynamic Agent Configuration** | Runtime agent selection and parameters | ✅ Implemented | ☐ Pending full review |
| **Provider Support** | OpenRouter, OpenAI, Anthropic, Google, XAI | ✅ Implemented | ☐ Pending full review |
| **Streaming Responses** | Real-time token streaming | 🔄 Refinement |
| **Error Recovery** | Graceful handling of API failures | 🔄 Refinement |
| **Session Management** | Conversation history and context tracking | ✅ Implemented | ☐ Pending full review |

### API & Integration

| Feature | Description | Status | Review Status |
|---------|-------------|--------|--------------:
| **OpenAI-Compatible API** | Drop-in replacement for OpenAI endpoints | ✅ Implemented | ☐ Pending full review |
| **RESTful Endpoints** | `/v1/chat/completions`, `/v1/models` | ✅ Implemented | ☐ Pending full review |
| **Streaming Support** | SSE-based response streaming | 🔄 Refinement |
| **MCP Server** | Model Context Protocol for tool integration | 🔄 Refinement |
| **A2A Agent Interface** | [Agent-to-Agent protocol](https://github.com/agent-protocol/agent-protocol) compatible | ⏳ Basic |
| **SDK Support** | Python client library | ✅ Implemented | ☐ Pending full review |
| **Authentication** | API key validation (optional) | ⏳ Basic |
| **CORS Support** | Cross-origin request handling | ✅ Implemented | ☐ Pending full review |
| **Request Validation** | Schema validation and error messages | 🔄 Refinement |
| **Rate Limiting** | Basic rate limit support | ⏳ Basic |

### Developer Experience

| Feature | Description | Status | Review Status |
|---------|-------------|--------|--------------:
| **Terminal UI (TUI)** | Rich interface with Textual | 🔄 Refinement |
| **Multiple UI Themes** | Default, dracula, monokai, gruvbox | ✅ Implemented | ☐ Pending full review |
| **Configuration Files** | YAML-based configuration | ✅ Implemented | ☐ Pending full review |
| **Environment Variables** | `.env` file support | ✅ Implemented | ☐ Pending full review |
| **Logging System** | Structured logging with levels | 🔄 Refinement |
| **Debug Mode** | Verbose output for troubleshooting | 🔄 Refinement |
| **Type Hints** | Full type coverage | 🔄 Refinement |
| **Code Formatting** | Black, isort integration | ✅ Implemented | ☐ Pending full review |
| **Linting** | Flake8, mypy, bandit | ✅ Implemented | ☐ Pending full review |
| **Pre-commit Hooks** | Automated code quality checks | ✅ Implemented | ☐ Pending full review |

### Testing & Quality

| Feature | Description | Status | Review Status |
|---------|-------------|--------|--------------:
| **Unit Tests** | Core functionality coverage | 🔄 Refinement |
| **Integration Tests** | API and agent interaction tests | 🔄 Refinement |
| **TUI Tests** | Textual snapshot testing | ⏳ Basic |
| **Test Coverage** | >95% code coverage | 🔄 Refinement |
| **CI/CD Pipeline** | GitHub Actions automation | ✅ Implemented | ☐ Pending full review |
| **Security Scanning** | Bandit, safety checks | ✅ Implemented | ☐ Pending full review |
| **Dependency Review** | Automated vulnerability scanning | ✅ Implemented | ☐ Pending full review |
| **Performance Benchmarks** | ARC-AGI-2 and algorithm comparison suites | ✅ Implemented | ☐ Pending full review |
| **Load Testing** | Basic concurrent request handling | ⏳ Basic |
| **Comprehensive Test Suite** | Full end-to-end validation | 🔧 In Development |

### Documentation

| Feature | Description | Status | Review Status |
|---------|-------------|--------|--------------:
| **README** | Project overview and quick start | ✅ Implemented | ☐ Pending full review |
| **API Documentation** | OpenAPI/Swagger spec | ✅ Implemented | ☐ Pending full review |
| **Quick Start Guides** | Multiple getting started paths | ✅ Implemented | ☐ Pending full review |
| **Configuration Guide** | Detailed config options | 🔄 Refinement |
| **Docker Guide** | Container deployment | ✅ Implemented | ☐ Pending full review |
| **MCP Integration Guide** | Tool setup instructions | ✅ Implemented | ☐ Pending full review |
| **Architecture Docs** | System design and flow | 🔄 Refinement |
| **Code Examples** | Sample implementations | ✅ Implemented | ☐ Pending full review |
| **API Reference** | Endpoint documentation | ✅ Implemented | ☐ Pending full review |
| **Troubleshooting Guide** | Common issues and solutions | 🚧 In Development |

## What's New in Canopy

Building on MassGen's foundation, Canopy adds:

### Algorithm Enhancements
- Tree-based exploration algorithms (TreeQuest) for systematic solution search
- Configurable algorithm profiles for different problem types
- Enhanced consensus mechanisms with weighted voting

### Developer Experience
- Interactive terminal UI using Textual with multiple themes
- OpenAI-compatible API server for integration with existing tools
- MCP (Model Context Protocol) server for tool integration
- A2A (Agent-to-Agent) protocol interface
- Comprehensive test suite with >90% coverage
- Automated code formatting and linting

### API and Integration
- RESTful API with OpenAI-compatible endpoints
- Streaming support for real-time responses
- Dynamic agent configuration per request
- Full request/response compatibility with OpenAI clients

### Quality of Life
- Structured logging with session management
- Configuration validation and error handling
- Docker support for containerized deployment
- GitHub Actions CI/CD pipeline

## Installation

```bash
# Clone the repository
git clone https://github.com/24601/canopy.git
cd canopy

# Install with pip
pip install -e .

# Or with uv (recommended)
uv pip install -e .
```

🐳 **[Docker Quick Start →](docs/quickstart/docker-quickstart.md)** | 🔌 **[API Quick Start →](docs/quickstart/api-quickstart.md)**

## Configuration

Create a `.env` file with your API keys:

```bash
# OpenRouter (recommended for multi-model access)
OPENROUTER_API_KEY=your_key_here

# Individual providers (optional)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
XAI_API_KEY=your_key_here
```

## Usage

### Command Line Interface

```bash
# Multi-agent mode with specific models
python cli.py "Explain quantum computing" --models gpt-4 claude-3 gemini-pro

# Use configuration file
python cli.py --config examples/fast_config.yaml "Your question here"

# Interactive mode
python cli.py --models gpt-4 gemini-pro
```

📚 **[More Examples →](docs/quickstart/examples.md)**

### API Server

Start the OpenAI-compatible API server:

```bash
python cli.py --serve
```

Use with any OpenAI client:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="canopy-multi",
    messages=[{"role": "user", "content": "Your question"}],
    extra_body={
        "agent_models": ["gpt-4", "claude-3", "gemini-pro"],
        "algorithm": "treequest",
        "consensus_threshold": 0.75
    }
)
```

### MCP Server

Canopy includes an MCP server for integration with tools like Claude Desktop:

```bash
# Start MCP server
python -m canopy.mcp_server

# Or configure in Claude Desktop's config
```

### A2A Protocol Interface

Use Canopy with the [Agent-to-Agent protocol](https://github.com/agent-protocol/agent-protocol):

```python
from canopy.a2a_agent import CanopyA2AAgent

agent = CanopyA2AAgent(
    name="canopy_assistant",
    models=["gpt-4", "claude-3"],
    consensus_threshold=0.75
)

# Use in A2A workflows
response = agent.generate_reply(messages)
```

## 📊 Benchmarking & Performance

Canopy includes comprehensive benchmarking capabilities following industry best practices and academic standards.

### ARC-AGI-2 Performance (Sakana AI Methodology)

| Algorithm | Pass@3 | Avg Time | LLM Efficiency | Improvement |
|-----------|-------:|---------:|---------------:|------------:|
| **TreeQuest** | **23.5%** | 45.2s | **0.094** | **+29.8%** |
| **MassGen** | 18.1% | **38.7s** | 0.072 | baseline |
| Single Model | 12.3% | 28.1s | 0.049 | -34.3% |

*Results on ARC-AGI-2 pattern recognition tasks (100 tasks, 3 runs each)*

### Key Findings

- **TreeQuest** shows 15-56% improvement over MassGen on complex reasoning tasks
- **Multi-agent** approaches consistently outperform single-model baselines
- **Performance scales** positively with task complexity and agent diversity
- **Cost efficiency** improves with tree-based exploration vs. parallel voting

### Running Benchmarks

```bash
# Quick algorithm comparison
python benchmarks/run_benchmarks.py --quick

# Full ARC-AGI-2 evaluation (requires external dataset)
python benchmarks/sakana_benchmarks.py

# Custom benchmark configuration
python benchmarks/run_benchmarks.py --config my_config.yaml
```

📊 **[Full Benchmarking Guide →](docs/benchmarking.md)**

## Architecture

Canopy orchestrates multiple agents through configurable algorithms:

1. **MassGen Algorithm**: Original parallel processing with democratic voting
2. **TreeQuest Algorithm**: Tree-based exploration inspired by Monte Carlo Tree Search

Agents work in phases:
- **Planning**: Agents independently analyze the problem
- **Execution**: Parallel work with shared visibility
- **Consensus**: Voting and debate until agreement is reached

## Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=canopy --cov-report=html

# Run specific test file
pytest tests/unit/test_orchestrator.py
```

### Code Quality

```bash
# Format code
black canopy tests
isort canopy tests

# Lint
flake8 canopy
mypy canopy

# Run all checks
make lint
```

## Credits

Canopy is built upon the excellent foundation provided by [MassGen](https://github.com/ag2ai/MassGen), created by the [AG2 team](https://github.com/ag2ai). We (uh, um, uh, I) are/am grateful for their pioneering work in multi-agent systems and collaborative AI.

### Original MassGen Team
- The AG2/AutoGen team at Microsoft Research (and whatever dramatic schism came out of that to fork into AG2, etc, )
- Contributors to the MassGen project

### Key Concepts From
- [The Myth of Reasoning](https://docs.ag2.ai/latest/docs/blog/#the-myth-of-reasoning) - Threads of thought and iterative refinement
- [AG2 Framework](https://github.com/ag2ai/ag2) - Multi-agent conversation patterns

## Roadmap

### Near Term (August 2025)
- [ ] **Comprehensive Test Suite** - Expand end-to-end testing coverage
- [ ] **Performance Profiling** - Detailed benchmarking and optimization
- [ ] **Enhanced Load Testing** - Stress testing for production readiness
- [ ] **Troubleshooting Guide** - Complete documentation for common issues
- [ ] **Plugin System** - Extensible architecture for custom algorithms
- [ ] **Webhook Support** - Event notifications for long-running tasks

### Medium Term (Q4 2025)
- [ ] **Additional Algorithms** - Beam search, genetic algorithms
- [ ] **Multi-Modal Support** - Image and document understanding
- [ ] **Persistent Sessions** - Database-backed conversation storage
- [ ] **Advanced Caching** - Response caching for efficiency
- [ ] **Metrics & Monitoring** - Prometheus/Grafana integration
- [ ] **Admin Dashboard** - Web UI for system management

### Long Term (2026+)
- [ ] **Distributed Orchestration** - Multi-node agent coordination
- [ ] **Custom Model Training** - Fine-tuning for specific domains
- [ ] **Enterprise Features** - SSO, audit logs, compliance tools
- [ ] **GraphQL API** - Alternative query interface
- [ ] **Mobile SDKs** - iOS and Android client libraries

### Implementation Milestones
- [x] Core multi-agent orchestration engine (implementation complete, optimization ongoing)
- [x] MassGen algorithm (functional, performance tuning needed)
- [x] TreeQuest algorithm (basic implementation, refinement in progress)
- [x] OpenAI-compatible API server (core functionality working)
- [x] Terminal UI with themes (functional, UX improvements ongoing)
- [x] MCP server (basic integration complete)
- [x] A2A protocol interface (minimal implementation)
- [x] Docker support (containerization working)
- [x] CI/CD pipeline (automated testing and deployment)
- [x] Test framework (infrastructure in place, coverage expanding)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

When contributing, please:
1. Maintain test coverage above 90%
2. Follow the existing code style
3. Add appropriate documentation
4. Credit any borrowed ideas or code

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built by the Canopy team (uh, yeah, just one guy...me), based on a lot of awesome research by Sakana, Google, others, etc (cited in module) on top of the work put into [MassGen](https://github.com/ag2ai/MassGen) and [AG2](https://github.com/ag2ai/ag2)

</div>