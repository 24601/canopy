# Algorithm extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen
# Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)
"""
Algorithm configuration profiles system.

This module provides a way to define and manage named configuration profiles
for algorithms, allowing users to easily select pre-configured setups like
"treequest-sakana" or "massgen-default" without specifying all parameters.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path  # noqa: TC003
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AlgorithmProfile:
    """Configuration profile for an algorithm.

    Attributes:
        name: Profile name (e.g., "treequest-sakana", "massgen-default")
        algorithm: Base algorithm to use ("massgen", "treequest")
        description: Human-readable description
        config: Algorithm-specific configuration
        models: List of model configurations for agents
        orchestrator_config: Orchestrator-level configuration
    """

    name: str
    algorithm: str
    description: str
    config: Dict[str, Any] = field(default_factory=dict)
    models: List[Dict[str, Any]] = field(default_factory=list)
    orchestrator_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlgorithmProfile":
        """Create profile from dictionary."""
        return cls(**data)


class ProfileRegistry:
    """Registry for algorithm profiles."""

    def __init__(self):
        """Initialize the profile registry."""
        self._profiles: Dict[str, AlgorithmProfile] = {}
        self._load_builtin_profiles()

    def _load_builtin_profiles(self):
        """Load built-in profiles."""
        # MassGen default profile
        self.register(
            AlgorithmProfile(
                name="massgen-default",
                algorithm="massgen",
                description="Default MassGen configuration with consensus voting",
                config={
                    "max_duration": 600,
                    "consensus_threshold": 0.5,
                    "max_debate_rounds": 3,
                    "status_check_interval": 1.0,
                    "thread_pool_timeout": 300,
                },
                models=[
                    {
                        "agent_type": "openai",
                        "model": "gpt-4o-mini",
                        "temperature": 0.7,
                    },
                    {
                        "agent_type": "openai",
                        "model": "gpt-4o-mini",
                        "temperature": 0.7,
                    },
                    {
                        "agent_type": "openai",
                        "model": "gpt-4o-mini",
                        "temperature": 0.7,
                    },
                ],
                orchestrator_config={"max_duration": 600, "consensus_threshold": 0.5},
            )
        )

        # TreeQuest Sakana profile
        self.register(
            AlgorithmProfile(
                name="treequest-sakana",
                algorithm="treequest",
                description="TreeQuest configuration matching Sakana AI paper (multi-model AB-MCTS)",
                config={
                    "max_iterations": 250,  # Matches paper's ~250 LLM calls
                    "max_depth": 10,
                    "branching_factor": 3,
                    "thompson_sampling_beta": 1.0,
                    "model_selection_strategy": "thompson_sampling",
                    "refinement_prompt_style": "sakana",
                    "enable_multi_model": True,
                },
                models=[
                    {
                        "agent_type": "openai",
                        "model": "gpt-4o-mini",
                        "temperature": 0.6,
                    },
                    {
                        "agent_type": "gemini",
                        "model": "gemini-2.5-pro",
                        "temperature": 0.6,
                    },
                    {
                        "agent_type": "openrouter",
                        "model": "deepseek/deepseek-r1-0528",
                        "temperature": 0.6,
                    },
                ],
                orchestrator_config={
                    "max_duration": 1200,
                    "algorithm": "treequest",
                },  # Longer for tree search
            )
        )

        # TreeQuest simple profile
        self.register(
            AlgorithmProfile(
                name="treequest-simple",
                algorithm="treequest",
                description="Simple TreeQuest with single model repeated sampling",
                config={
                    "max_iterations": 50,
                    "max_depth": 5,
                    "branching_factor": 2,
                    "thompson_sampling_beta": 0.5,
                    "model_selection_strategy": "fixed",
                    "enable_multi_model": False,
                },
                models=[
                    {"agent_type": "openai", "model": "gpt-4o", "temperature": 0.8},
                    {"agent_type": "openai", "model": "gpt-4o", "temperature": 0.8},
                ],
                orchestrator_config={"max_duration": 300, "algorithm": "treequest"},
            )
        )

        # MassGen diverse profile
        self.register(
            AlgorithmProfile(
                name="massgen-diverse",
                algorithm="massgen",
                description="MassGen with diverse model ensemble",
                config={
                    "max_duration": 900,
                    "consensus_threshold": 0.6,
                    "max_debate_rounds": 5,
                    "enable_model_diversity_bonus": True,
                },
                models=[
                    {"agent_type": "openai", "model": "gpt-4o", "temperature": 0.7},
                    {
                        "agent_type": "gemini",
                        "model": "gemini-2.5-pro",
                        "temperature": 0.7,
                    },
                    {"agent_type": "grok", "model": "grok-4", "temperature": 0.7},
                    {
                        "agent_type": "openrouter",
                        "model": "deepseek/deepseek-r1",
                        "temperature": 0.7,
                    },
                ],
                orchestrator_config={"max_duration": 900, "consensus_threshold": 0.6},
            )
        )

    def register(self, profile: AlgorithmProfile) -> None:
        """Register a profile.

        Args:
            profile: Profile to register
        """
        if profile.name in self._profiles:
            logger.warning(f"Overwriting existing profile: {profile.name}")

        self._profiles[profile.name] = profile
        logger.info(f"Registered profile: {profile.name}")

    def get(self, name: str) -> Optional[AlgorithmProfile]:
        """Get a profile by name.

        Args:
            name: Profile name

        Returns:
            Profile if found, None otherwise
        """
        return self._profiles.get(name)

    def list_profiles(self) -> List[str]:
        """List all available profile names."""
        return list(self._profiles.keys())

    def get_profiles_for_algorithm(self, algorithm: str) -> List[str]:
        """Get profiles for a specific algorithm.

        Args:
            algorithm: Algorithm name (e.g., "massgen", "treequest")

        Returns:
            List of profile names for that algorithm
        """
        return [name for name, profile in self._profiles.items() if profile.algorithm == algorithm]

    def load_from_file(self, path: Path) -> None:
        """Load profiles from a JSON file.

        Args:
            path: Path to JSON file containing profiles
        """
        with open(path) as f:
            data = json.load(f)

        # Handle single profile or list of profiles
        profiles = data if isinstance(data, list) else [data]

        for profile_data in profiles:
            profile = AlgorithmProfile.from_dict(profile_data)
            self.register(profile)

    def save_to_file(self, path: Path, profile_names: Optional[List[str]] = None) -> None:
        """Save profiles to a JSON file.

        Args:
            path: Path to save JSON file
            profile_names: Specific profiles to save (None for all)
        """
        if profile_names is None:
            profiles = list(self._profiles.values())
        else:
            profiles = [self._profiles[name] for name in profile_names if name in self._profiles]

        data = [profile.to_dict() for profile in profiles]

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def describe_profile(self, name: str) -> str:
        """Get a detailed description of a profile.

        Args:
            name: Profile name

        Returns:
            Formatted description string
        """
        profile = self.get(name)
        if not profile:
            return f"Profile '{name}' not found"

        lines = [
            f"Profile: {profile.name}",
            f"Algorithm: {profile.algorithm}",
            f"Description: {profile.description}",
            "",
            "Configuration:",
        ]

        for key, value in profile.config.items():
            lines.append(f"  {key}: {value}")

        lines.extend(["", f"Models ({len(profile.models)} agents):"])

        for i, model in enumerate(profile.models, 1):
            model_str = f"  Agent {i}: {model['model']} ({model['agent_type']})"
            if "temperature" in model:
                model_str += f" @ temp={model['temperature']}"
            lines.append(model_str)

        return "\n".join(lines)


# Global registry instance
_profile_registry = ProfileRegistry()


def get_profile(name: str) -> Optional[AlgorithmProfile]:
    """Get a profile from the global registry."""
    return _profile_registry.get(name)


def list_profiles() -> List[str]:
    """List all available profiles."""
    return _profile_registry.list_profiles()


def register_profile(profile: AlgorithmProfile) -> None:
    """Register a profile in the global registry."""
    _profile_registry.register(profile)


def load_profiles_from_file(path: Path) -> None:
    """Load profiles from a file into the global registry."""
    _profile_registry.load_from_file(path)


def describe_profile(name: str) -> str:
    """Get a detailed description of a profile."""
    return _profile_registry.describe_profile(name)
