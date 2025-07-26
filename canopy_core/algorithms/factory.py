# Algorithm extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen

# Algorithm extensions for Canopy
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen
# Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)
"""
Factory pattern for creating orchestration algorithms.

This module provides a factory for creating algorithm instances based on
configuration, allowing for easy extension with new algorithms.
"""

from typing import Any, Dict, Type

from .base import BaseAlgorithm

# Registry of available algorithms
_ALGORITHM_REGISTRY: Dict[str, Type[BaseAlgorithm]] = {}


def register_algorithm(name: str, algorithm_class: Type[BaseAlgorithm]) -> None:
    """Register an algorithm class with the factory.

    Args:
        name: Name identifier for the algorithm
        algorithm_class: The algorithm class to register
    """
    if name in _ALGORITHM_REGISTRY:
        raise ValueError(f"Algorithm '{name}' is already registered")

    if not issubclass(algorithm_class, BaseAlgorithm):
        raise TypeError("Algorithm class must inherit from BaseAlgorithm")

    _ALGORITHM_REGISTRY[name] = algorithm_class


def get_available_algorithms() -> list[str]:
    """Get list of available algorithm names.

    Returns:
        List of registered algorithm names
    """
    return list(_ALGORITHM_REGISTRY.keys())


class AlgorithmFactory:
    """Factory for creating orchestration algorithm instances."""

    @staticmethod
    def create(
        algorithm_name: str,
        agents: Dict[int, Any],
        agent_states: Dict[int, Any],
        system_state: Any,
        config: Dict[str, Any],
        log_manager: Any = None,
        streaming_orchestrator: Any = None,
    ) -> BaseAlgorithm:
        """Create an algorithm instance.

        Args:
            algorithm_name: Name of the algorithm to create
            agents: Dictionary mapping agent IDs to agent instances
            agent_states: Dictionary mapping agent IDs to their states
            system_state: Shared system state
            config: Algorithm-specific configuration
            log_manager: Optional log manager
            streaming_orchestrator: Optional streaming display

        Returns:
            Instance of the requested algorithm

        Raises:
            ValueError: If algorithm name is not registered
        """
        if algorithm_name not in _ALGORITHM_REGISTRY:
            available = ", ".join(_ALGORITHM_REGISTRY.keys())
            raise ValueError(f"Unknown algorithm '{algorithm_name}'. " f"Available algorithms: {available}")

        algorithm_class = _ALGORITHM_REGISTRY[algorithm_name]

        return algorithm_class(
            agents=agents,
            agent_states=agent_states,
            system_state=system_state,
            config=config,
            log_manager=log_manager,
            streaming_orchestrator=streaming_orchestrator,
        )
