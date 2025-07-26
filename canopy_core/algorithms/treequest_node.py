# Algorithm extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen

"""
TreeQuest tree node implementation.

Based on Sakana AI's TreeQuest paper (arXiv:2503.04412).
"""

import dataclasses
from typing import Any, Dict, Generic, List, Optional, TypeVar

import numpy as np
from scipy import stats

StateT = TypeVar("StateT")


@dataclasses.dataclass
class Node(Generic[StateT]):
    """A node in the TreeQuest search tree.

    Each node represents a state in the search process, with optional parent/children
    relationships and associated scores.
    """

    state: Optional[StateT] = None  # The actual content/response at this node
    score: float = -1.0  # Root has -1.0, others 0-1
    expand_idx: int = -1  # Root has -1, then 0,1,2... for order of expansion
    parent: Optional["Node[StateT]"] = None
    children: List["Node[StateT]"] = dataclasses.field(default_factory=list)

    # Additional metadata for multi-agent scenarios
    agent_id: Optional[int] = None  # Which agent generated this node
    action_type: str = "GEN"  # GEN (generate new) or CONT (continue/refine)
    depth: int = 0  # Depth in the tree
    node_id: int = dataclasses.field(default_factory=lambda: id(object()))  # Unique ID for hashing

    def add_child(self, child: "Node[StateT]") -> None:
        """Add a child node."""
        child.parent = self
        child.depth = self.depth + 1
        child.expand_idx = len(self.children)
        self.children.append(child)

    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0

    def get_path_to_root(self) -> List["Node[StateT]"]:
        """Get the path from this node to the root."""
        path = []
        current = self
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))

    def get_best_leaf(self) -> "Node[StateT]":
        """Find the best scoring leaf node in the subtree."""
        if self.is_leaf():
            return self

        best_leaf = None
        best_score = -1.0

        def visit(node):
            nonlocal best_leaf, best_score
            if node.is_leaf() and node.score > best_score:
                best_leaf = node
                best_score = node.score
            for child in node.children:
                visit(child)

        visit(self)
        return best_leaf

    def __hash__(self) -> int:
        """Make Node hashable by using its unique node_id."""
        return hash(self.node_id)

    def __eq__(self, other) -> bool:
        """Nodes are equal if they have the same node_id."""
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id


class ProbabilisticDist:
    """Probabilistic distribution for Thompson sampling.

    Supports both Beta distribution (for bounded rewards) and
    Gaussian with inverse-gamma prior (for unbounded rewards).
    """

    def __init__(self, use_beta: bool = True, alpha: float = 1.0, beta_param: float = 1.0):
        """Initialize the distribution.

        Args:
            use_beta: If True, use Beta distribution. Otherwise use Gaussian.
            alpha: Alpha parameter for Beta distribution
            beta_param: Beta parameter for Beta distribution
        """
        self.use_beta = use_beta

        if use_beta:
            # Beta distribution parameters
            self.alpha = alpha
            self.beta = beta_param
        else:
            # Gaussian with inverse-gamma prior parameters
            self.mu_0 = 0.5  # Prior mean
            self.kappa_0 = 1.0  # Prior precision of mean
            self.alpha_0 = 2.0  # Shape parameter for inverse-gamma
            self.beta_0 = 1.0  # Scale parameter for inverse-gamma
            self.n = 0  # Number of observations
            self.sum_x = 0.0  # Sum of observations
            self.sum_x_sq = 0.0  # Sum of squared observations

    def update(self, reward: float) -> None:
        """Update the distribution with a new observation."""
        if self.use_beta:
            # Beta distribution update
            if reward > 0.5:  # Success
                self.alpha += 1
            else:  # Failure
                self.beta += 1
        else:
            # Gaussian update
            self.n += 1
            self.sum_x += reward
            self.sum_x_sq += reward**2

    def sample(self) -> float:
        """Sample from the posterior distribution."""
        if self.use_beta:
            return np.random.beta(self.alpha, self.beta)
        else:
            # Posterior parameters for Gaussian
            if self.n == 0:
                return np.random.normal(self.mu_0, 1.0 / np.sqrt(self.kappa_0))

            x_bar = self.sum_x / self.n
            kappa_n = self.kappa_0 + self.n
            mu_n = (self.kappa_0 * self.mu_0 + self.n * x_bar) / kappa_n
            alpha_n = self.alpha_0 + self.n / 2
            beta_n = (
                self.beta_0
                + 0.5 * (self.sum_x_sq - self.n * x_bar**2)
                + 0.5 * self.kappa_0 * self.n * (x_bar - self.mu_0) ** 2 / kappa_n
            )

            # Sample precision from inverse-gamma
            precision = np.random.gamma(alpha_n, 1.0 / beta_n)
            # Sample mean from normal
            return np.random.normal(mu_n, 1.0 / np.sqrt(kappa_n * precision))

    def get_mean(self) -> float:
        """Get the expected value of the distribution."""
        if self.use_beta:
            return self.alpha / (self.alpha + self.beta)
        else:
            if self.n == 0:
                return self.mu_0
            return (self.kappa_0 * self.mu_0 + self.sum_x) / (self.kappa_0 + self.n)


class ThompsonState:
    """Thompson sampling state for adaptive branching decisions."""

    def __init__(self, actions: List[str], use_beta: bool = True):
        """Initialize Thompson sampling state.

        Args:
            actions: List of possible actions (e.g., agent IDs or model names)
            use_beta: Whether to use Beta distribution
        """
        self.actions = actions
        self.use_beta = use_beta

        # Action-level probability distributions
        self.action_probas = {action: ProbabilisticDist(use_beta) for action in actions}

        # GEN vs CONT decision distributions
        self.gen_vs_cont_probas = {
            "GEN": ProbabilisticDist(use_beta),
            "CONT": ProbabilisticDist(use_beta),
        }

        # Node-level distributions for CONT decisions
        self.node_probas: Dict[Node, ProbabilisticDist] = {}

    def update_action_reward(self, action: str, reward: float) -> None:
        """Update reward for a specific action."""
        if action in self.action_probas:
            self.action_probas[action].update(reward)

    def update_gen_cont_reward(self, action_type: str, reward: float) -> None:
        """Update reward for GEN or CONT decision."""
        if action_type in self.gen_vs_cont_probas:
            self.gen_vs_cont_probas[action_type].update(reward)

    def update_node_reward(self, node: Node, reward: float) -> None:
        """Update reward for a specific node (for CONT decisions)."""
        if node not in self.node_probas:
            self.node_probas[node] = ProbabilisticDist(self.use_beta)
        self.node_probas[node].update(reward)

    def thompson_sample_action(self) -> str:
        """Sample an action using Thompson sampling."""
        samples = {action: dist.sample() for action, dist in self.action_probas.items()}
        return max(samples, key=samples.get)

    def thompson_sample_gen_cont(self) -> str:
        """Sample GEN or CONT decision using Thompson sampling."""
        gen_sample = self.gen_vs_cont_probas["GEN"].sample()
        cont_sample = self.gen_vs_cont_probas["CONT"].sample()
        return "GEN" if gen_sample >= cont_sample else "CONT"

    def thompson_sample_node(self, nodes: List[Node]) -> Optional[Node]:
        """Sample a node for CONT using Thompson sampling."""
        if not nodes:
            return None

        # Only consider nodes we have distributions for
        valid_nodes = [n for n in nodes if n in self.node_probas]
        if not valid_nodes:
            return None

        samples = {node: self.node_probas[node].sample() for node in valid_nodes}
        return max(samples, key=samples.get)
