"""
Multi-Agent Orchestration Algorithms

This module provides different algorithms for orchestrating multi-agent collaboration.
Each algorithm implements the same interface but uses different strategies for:
- Agent coordination
- Consensus building  
- Task completion

Supported Algorithms:
- default: Original MassGen collaborative algorithm
- arxiv_2503_04412: Algorithm based on "Multi-Agent Reasoning" paper
"""

from .base import Algorithm
from .default import DefaultAlgorithm

# Algorithm registry for easy creation
ALGORITHMS = {
    "default": DefaultAlgorithm,
    "collaborative": DefaultAlgorithm,  # Alias for backward compatibility
}

def create_algorithm(algorithm_name: str, **kwargs) -> Algorithm:
    """
    Create an algorithm instance by name.
    
    Args:
        algorithm_name: Name of the algorithm to create
        **kwargs: Algorithm-specific configuration parameters
        
    Returns:
        Algorithm instance
        
    Raises:
        ValueError: If algorithm name is not supported
    """
    if algorithm_name not in ALGORITHMS:
        available = list(ALGORITHMS.keys())
        raise ValueError(f"Unknown algorithm: {algorithm_name}. Available: {available}")
    
    algorithm_class = ALGORITHMS[algorithm_name]
    return algorithm_class(**kwargs)

def get_available_algorithms():
    """Get list of available algorithm names."""
    return list(ALGORITHMS.keys())

__all__ = [
    "Algorithm",
    "DefaultAlgorithm", 
    "create_algorithm",
    "get_available_algorithms",
    "ALGORITHMS"
]