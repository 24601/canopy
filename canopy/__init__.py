"""
Canopy: Multi-Agent Consensus through Tree-Based Exploration

Built upon the foundation of MassGen by the AG2 team.
"""

__version__ = "1.0.0"

# Import key components
from canopy_core import (
    MassConfig,
    MassSystem,
    create_config_from_models,
    load_config_from_yaml,
    run_mass_agents,
    run_mass_with_config,
)

# Import Canopy-specific components
from .a2a_agent import CanopyA2AAgent, AgentCard, A2AMessage, A2AResponse

__all__ = [
    # Core functionality from MassGen
    "MassConfig",
    "MassSystem", 
    "create_config_from_models",
    "load_config_from_yaml",
    "run_mass_agents",
    "run_mass_with_config",
    
    # Canopy additions
    "CanopyA2AAgent",
    "AgentCard",
    "A2AMessage", 
    "A2AResponse",
    "__version__",
]

# Credits to original authors
__credits__ = """
Canopy is built upon MassGen (https://github.com/ag2ai/MassGen)
Original work by the AG2 team at Microsoft Research
"""