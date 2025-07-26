# Algorithm extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen

# Algorithm extensions for Canopy
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen
"""
Orchestration algorithms for the Canopy framework.

This package contains pluggable orchestration algorithms that can be used
to coordinate multi-agent systems. Each algorithm implements the BaseAlgorithm
interface and provides its own strategy for agent coordination.
"""

from .base import AlgorithmResult, BaseAlgorithm
from .canopy_algorithm import CanopyAlgorithm
from .factory import AlgorithmFactory, register_algorithm
from .treequest_algorithm import TreeQuestAlgorithm

__all__ = [
    "BaseAlgorithm",
    "AlgorithmResult",
    "AlgorithmFactory",
    "register_algorithm",
    "CanopyAlgorithm",
    "TreeQuestAlgorithm",
]
