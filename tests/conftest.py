"""Pytest configuration and fixtures."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Disable logging during tests unless explicitly needed
import logging

logging.disable(logging.CRITICAL)


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    agent = Mock()
    agent.agent_id = 1
    agent.model = "test-model"
    agent.state = Mock()
    agent.process_message = Mock(return_value=Mock(text="Test response", code=[], citations=[]))
    agent.work_on_task = Mock(return_value=[])
    return agent


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator for testing."""
    orchestrator = Mock()
    orchestrator.agents = {}
    orchestrator.agent_states = {}
    orchestrator.system_state = Mock()
    orchestrator.log_manager = Mock()
    orchestrator.streaming_orchestrator = Mock()
    return orchestrator


@pytest.fixture
def mock_task():
    """Create a mock task for testing."""
    from canopy_core.types import TaskInput

    return TaskInput(question="What is 2+2?", task_id="test-task-123", context={})


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    from canopy_core.types import AgentConfig, MassConfig, ModelConfig, OrchestratorConfig

    model_config = ModelConfig(
        model="test-model", tools=["test_tool"], max_retries=3, max_rounds=5, inference_timeout=30
    )

    agent_config = AgentConfig(agent_id=1, agent_type="openai", model_config=model_config)

    orchestrator_config = OrchestratorConfig(max_duration=60, consensus_threshold=0.5, algorithm="massgen")

    return MassConfig(orchestrator=orchestrator_config, agents=[agent_config])


@pytest.fixture(autouse=True)
def reset_algorithm_registry():
    """Reset the algorithm registry after each test."""
    from canopy_core.algorithms.factory import _ALGORITHM_REGISTRY

    # Save original state
    original = _ALGORITHM_REGISTRY.copy()

    yield

    # Restore original state
    _ALGORITHM_REGISTRY.clear()
    _ALGORITHM_REGISTRY.update(original)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files."""
    return tmp_path


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test-openai-key",
        "GEMINI_API_KEY": "test-gemini-key",
        "GROK_API_KEY": "test-grok-key",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


# Markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_api_key: mark test as requiring API keys")
