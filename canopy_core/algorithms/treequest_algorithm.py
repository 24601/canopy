# Algorithm extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen
# Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)
"""
TreeQuest algorithm implementation.

This module implements the Adaptive Branching Monte Carlo Tree Search (AB-MCTS)
algorithm from Sakana AI's TreeQuest paper (arXiv:2503.04412).

Reference:
    Sakana AI (2025). "TreeQuest: Adaptive Branching Monte Carlo Tree Search
    for Inference-Time Scaling." arXiv preprint arXiv:2503.04412.
    https://arxiv.org/abs/2503.04412
"""

import logging
import random
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..tracing import add_span_attributes, traced
from ..types import AgentResponse, TaskInput  # noqa: TC001
from .base import AlgorithmResult, BaseAlgorithm
from .factory import register_algorithm
from .treequest_node import Node, ThompsonState

logger = logging.getLogger(__name__)


class TreeQuestState:
    """State object for a TreeQuest node.

    Contains the actual response text and metadata about how it was generated.
    """

    def __init__(self, text: str, agent_id: int, parent_state: Optional["TreeQuestState"] = None):
        self.text = text
        self.agent_id = agent_id
        self.parent_state = parent_state
        self.metadata = {}

    def __str__(self) -> str:
        return self.text


class TreeQuestAlgorithm(BaseAlgorithm):
    """TreeQuest AB-MCTS orchestration algorithm.

    This algorithm implements the Adaptive Branching Monte Carlo Tree Search
    approach where:
    1. The algorithm builds a search tree of candidate solutions
    2. At each step, it decides whether to "go deeper" (refine) or "go wider" (generate)
    3. Uses Thompson sampling to balance exploration vs exploitation
    4. For multi-LLM, it also selects which model to use based on performance

    Implementation based on:
    "TreeQuest: Adaptive Branching Monte Carlo Tree Search for Inference-Time Scaling"
    by Sakana AI (arXiv:2503.04412, 2025)
    """

    def __init__(
        self,
        agents: Dict[int, Any],
        agent_states: Dict[int, Any],
        system_state: Any,
        config: Dict[str, Any],
        log_manager: Any = None,
        streaming_orchestrator: Any = None,
    ) -> None:
        """Initialize the TreeQuest algorithm."""
        super().__init__(
            agents,
            agent_states,
            system_state,
            config,
            log_manager,
            streaming_orchestrator,
        )

        # Algorithm-specific configuration
        self.max_iterations = config.get("max_iterations", 20)
        self.max_depth = config.get("max_depth", 5)
        self.branching_factor = config.get("branching_factor", 3)
        self.use_beta_distribution = config.get("use_beta_distribution", True)
        self.exploration_weight = config.get("exploration_weight", 1.0)

        # Multi-LLM selection strategy
        self.model_selection_strategy = config.get(
            "model_selection_strategy", "thompson"
        )  # thompson, ucb, or round_robin

        # Search tree state
        self.root_node: Optional[Node[TreeQuestState]] = None
        self.thompson_state: Optional[ThompsonState] = None
        self.iteration_count = 0
        self.all_rewards_store: Dict[str, List[float]] = {}

        # Track best paths for synthesis
        self.best_leaves: List[Node[TreeQuestState]] = []
        self.final_response = None

        logger.info("🌳 TreeQuest algorithm initialized with AB-MCTS")

    def get_algorithm_name(self) -> str:
        """Return the algorithm name."""
        return "treequest"

    def validate_config(self) -> bool:
        """Validate the algorithm configuration."""
        if self.max_iterations <= 0:
            raise ValueError("Max iterations must be positive")

        if self.max_depth <= 0:
            raise ValueError("Max depth must be positive")

        if self.branching_factor <= 0:
            raise ValueError("Branching factor must be positive")

        return True

    @traced("treequest_algorithm_run")
    def run(self, task: TaskInput) -> AlgorithmResult:
        """Run the TreeQuest AB-MCTS algorithm."""
        logger.info("🌳 Starting TreeQuest AB-MCTS algorithm")

        add_span_attributes(
            {
                "algorithm.name": "treequest",
                "task.id": task.task_id,
                "agents.count": len(self.agents),
                "max_iterations": self.max_iterations,
                "model_selection_strategy": self.model_selection_strategy,
            }
        )

        start_time = time.time()

        # Initialize task and tree
        self._initialize_task(task)

        # Run AB-MCTS iterations
        for i in range(self.max_iterations):
            self.iteration_count = i + 1
            logger.info(f"🔄 TreeQuest iteration {i+1}/{self.max_iterations}")

            # Update UI to show iteration
            if self.streaming_orchestrator:
                self.streaming_orchestrator.add_system_message(f"🔄 Iteration {i+1}/{self.max_iterations}")

            # Perform one MCTS step
            self._mcts_step(task)

            # Check for early stopping
            if self._should_stop_early():
                logger.info("🛑 Early stopping triggered")
                break

        # Synthesize final response from the search tree
        self._synthesize_response()

        # Calculate session duration
        end_time = time.time()
        session_duration = end_time - start_time

        return self._finalize_session(session_duration)

    def _initialize_task(self, task: TaskInput) -> None:
        """Initialize the system for a new task."""
        logger.info(f"🎯 Initializing TreeQuest AB-MCTS for task: {task.task_id}")

        self.system_state.task = task
        self.system_state.start_time = time.time()
        self.system_state.phase = "tree_search"
        self.final_response = None

        # Initialize root node
        self.root_node = Node[TreeQuestState]()
        self.root_node.state = TreeQuestState("[ROOT]", -1)

        # Initialize Thompson sampling state
        agent_actions = [str(agent_id) for agent_id in self.agents.keys()]
        self.thompson_state = ThompsonState(agent_actions, self.use_beta_distribution)

        # Initialize rewards store for each agent
        for agent_id in self.agents:
            self.all_rewards_store[str(agent_id)] = []

        # Initialize agent states
        for agent_id in self.agents:
            self.agent_states[agent_id].status = "ready"
            self.agent_states[agent_id].round = 0
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_status(agent_id, "ready")

        # Initialize streaming display
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("unknown", "tree_search")
            init_msg = f"🌳 Starting TreeQuest AB-MCTS with {len(self.agents)} agents"
            self.streaming_orchestrator.add_system_message(init_msg)

    def _mcts_step(self, task: TaskInput) -> None:
        """Perform one MCTS iteration: selection, expansion, evaluation, backpropagation."""

        # Step 1: Selection - decide whether to go wider (GEN) or deeper (CONT)
        action_type = self._select_action_type()

        if action_type == "GEN":
            # Generate new response from scratch
            node = self._select_node_for_expansion()
            agent_id = self._select_agent()

            # Generate new response
            new_node = self._generate_new_response(node, agent_id, task)

            # Backpropagate the result
            if new_node:
                self._backpropagate(new_node, new_node.score, str(agent_id), "GEN")

        else:  # CONT
            # Continue/refine existing response
            node = self._select_node_for_continuation()
            if node and node.state.agent_id != -1:  # Not root
                agent_id = self._select_agent()

                # Generate refined response
                refined_node = self._refine_response(node, agent_id, task)

                # Backpropagate the result
                if refined_node:
                    self._backpropagate(refined_node, refined_node.score, str(agent_id), "CONT")

    def _select_action_type(self) -> str:
        """Decide whether to generate new (GEN) or continue existing (CONT)."""
        # For first few iterations, always generate new
        if self.iteration_count <= 3:
            return "GEN"

        # Use Thompson sampling to decide
        action_type = self.thompson_state.thompson_sample_gen_cont()

        logger.info(f"🎲 Selected action type: {action_type}")
        return action_type

    def _select_agent(self) -> int:
        """Select which agent/LLM to use based on the strategy."""
        if self.model_selection_strategy == "thompson":
            agent_str = self.thompson_state.thompson_sample_action()
            agent_id = int(agent_str)
        elif self.model_selection_strategy == "ucb":
            agent_id = self._select_agent_ucb()
        else:  # round_robin
            agent_id = (self.iteration_count % len(self.agents)) + 1

        logger.info(f"🤖 Selected agent {agent_id} ({self.agents[agent_id].model})")
        return agent_id

    def _select_agent_ucb(self) -> int:
        """Select agent using Upper Confidence Bound."""
        best_agent = None
        best_ucb = -float("inf")

        for agent_id in self.agents:
            rewards = self.all_rewards_store.get(str(agent_id), [])
            if not rewards:
                # Unexplored agent - select it
                return agent_id

            mean_reward = np.mean(rewards)
            n_tries = len(rewards)
            total_tries = sum(len(self.all_rewards_store.get(str(a), [])) for a in self.agents)

            # UCB formula
            ucb = mean_reward + self.exploration_weight * np.sqrt(2 * np.log(total_tries) / n_tries)

            if ucb > best_ucb:
                best_ucb = ucb
                best_agent = agent_id

        return best_agent or 1

    def _select_node_for_expansion(self) -> Node[TreeQuestState]:
        """Select a node to expand (add children to)."""
        # Find all leaf nodes that haven't reached max depth
        candidates = []

        def collect_expandable(node: Node[TreeQuestState], depth: int):
            if depth < self.max_depth and node.is_leaf():
                candidates.append(node)
            for child in node.children:
                collect_expandable(child, depth + 1)

        collect_expandable(self.root_node, 0)

        if not candidates:
            return self.root_node

        # Select node with highest potential (could use UCB here too)
        # For now, prefer nodes with higher scores
        return max(candidates, key=lambda n: n.score if n.score >= 0 else 0.5)

    def _select_node_for_continuation(self) -> Optional[Node[TreeQuestState]]:
        """Select a node to continue/refine using Thompson sampling."""
        # Collect all non-root nodes
        all_nodes = []

        def collect_nodes(node: Node[TreeQuestState]):
            if node != self.root_node:
                all_nodes.append(node)
            for child in node.children:
                collect_nodes(child)

        collect_nodes(self.root_node)

        if not all_nodes:
            return None

        # Use Thompson sampling to select
        selected = self.thompson_state.thompson_sample_node(all_nodes)
        if not selected:
            # Fallback to random selection
            selected = random.choice(all_nodes)

        return selected

    def _generate_new_response(
        self, parent_node: Node[TreeQuestState], agent_id: int, task: TaskInput
    ) -> Optional[Node[TreeQuestState]]:
        """Generate a new response from an agent."""
        try:
            # Update agent state
            self.agent_states[agent_id].status = "working"
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_status(agent_id, "working")
                self.streaming_orchestrator.add_system_message(f"🆕 Agent {agent_id} generating new response...")

            # Prepare prompt
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Provide a clear and comprehensive answer."},
                {"role": "user", "content": task.question},
            ]

            # Generate response
            agent = self.agents[agent_id]
            result = agent.process_message(messages)

            # Evaluate the response (simple length-based scoring for now)
            score = self._evaluate_response(result.text, task)

            # Create new node
            new_state = TreeQuestState(
                result.text, agent_id, parent_node.state if parent_node != self.root_node else None
            )
            new_node = Node[TreeQuestState](state=new_state, score=score, agent_id=agent_id, action_type="GEN")
            parent_node.add_child(new_node)

            # Update agent state
            self.agent_states[agent_id].status = "completed"
            self.agent_states[agent_id].update_count += 1
            self.agent_states[agent_id].latest_answer = result.text

            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_status(agent_id, "completed")
                self.streaming_orchestrator.add_system_message(
                    f"✅ Agent {agent_id} generated response (score: {score:.3f})"
                )

            return new_node

        except Exception as e:
            logger.error(f"❌ Agent {agent_id} failed to generate: {e}")
            self.mark_agent_failed(agent_id, str(e))
            return None

    def _refine_response(
        self, node: Node[TreeQuestState], agent_id: int, task: TaskInput
    ) -> Optional[Node[TreeQuestState]]:
        """Refine an existing response."""
        try:
            # Update agent state
            self.agent_states[agent_id].status = "working"
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_status(agent_id, "working")
                self.streaming_orchestrator.add_system_message(f"🔧 Agent {agent_id} refining existing response...")

            # Prepare refinement prompt
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Improve and refine the given answer."},
                {
                    "role": "user",
                    "content": f"Question: {task.question}\n\nPrevious answer:\n{node.state.text}\n\nPlease improve this answer by making it more comprehensive, accurate, and clear.",
                },
            ]

            # Generate refined response
            agent = self.agents[agent_id]
            result = agent.process_message(messages)

            # Evaluate the refined response
            score = self._evaluate_response(result.text, task)

            # Create new node as child
            new_state = TreeQuestState(result.text, agent_id, node.state)
            new_node = Node[TreeQuestState](state=new_state, score=score, agent_id=agent_id, action_type="CONT")
            node.add_child(new_node)

            # Update agent state
            self.agent_states[agent_id].status = "completed"
            self.agent_states[agent_id].update_count += 1
            self.agent_states[agent_id].latest_answer = result.text

            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_status(agent_id, "completed")
                self.streaming_orchestrator.add_system_message(
                    f"✅ Agent {agent_id} refined response (score: {score:.3f})"
                )

            return new_node

        except Exception as e:
            logger.error(f"❌ Agent {agent_id} failed to refine: {e}")
            self.mark_agent_failed(agent_id, str(e))
            return None

    def _evaluate_response(self, response: str, task: TaskInput) -> float:
        """Evaluate a response and return a score between 0 and 1.

        In a real implementation, this could use:
        - An external evaluator/judge model
        - Task-specific metrics
        - Human feedback

        For now, we use simple heuristics.
        """
        # Simple scoring based on response characteristics
        score = 0.5  # Base score

        # Length bonus (normalized)
        length = len(response)
        if length > 100:
            score += 0.1
        if length > 300:
            score += 0.1

        # Completeness indicators
        if "?" in task.question and any(
            indicator in response.lower() for indicator in ["therefore", "thus", "in conclusion", "answer"]
        ):
            score += 0.1

        # Variety bonus (unique words ratio)
        words = response.lower().split()
        if words:
            unique_ratio = len(set(words)) / len(words)
            score += 0.1 * unique_ratio

        # Cap at 1.0
        return min(score, 1.0)

    def _backpropagate(self, node: Node[TreeQuestState], score: float, agent_id: str, action_type: str) -> None:
        """Backpropagate the score up the tree and update Thompson sampling states."""
        # Update agent rewards
        self.all_rewards_store[agent_id].append(score)
        self.thompson_state.update_action_reward(agent_id, score)

        # Update GEN/CONT rewards
        self.thompson_state.update_gen_cont_reward(action_type, score)

        # Update node rewards for Thompson sampling
        current = node
        while current.parent is not None:
            self.thompson_state.update_node_reward(current, score)
            current = current.parent

        # Track best leaves
        if node.is_leaf() and score > 0.7:  # High-quality threshold
            self.best_leaves.append(node)
            self.best_leaves.sort(key=lambda n: n.score, reverse=True)
            self.best_leaves = self.best_leaves[:5]  # Keep top 5

    def _should_stop_early(self) -> bool:
        """Check if we should stop early based on convergence or quality."""
        # Stop if we have high-quality responses
        if self.best_leaves and self.best_leaves[0].score > 0.9:
            return True

        # Stop if agents are consistently failing
        failed_count = sum(1 for state in self.agent_states.values() if state.status == "failed")
        if failed_count >= len(self.agents) - 1:
            return True

        return False

    def _synthesize_response(self) -> None:
        """Synthesize the final response from the search tree.

        Unlike traditional MCTS that picks a single winner, TreeQuest
        synthesizes insights from multiple high-quality paths.
        """
        logger.info("🎯 Synthesizing final response from search tree")

        # Find all high-quality leaf nodes
        all_leaves = []

        def collect_leaves(node: Node[TreeQuestState]):
            if node.is_leaf() and node.score > 0.6:  # Quality threshold
                all_leaves.append(node)
            for child in node.children:
                collect_leaves(child)

        collect_leaves(self.root_node)

        if not all_leaves:
            # Fallback to any leaf
            all_leaves = []

            def collect_any_leaf(node: Node[TreeQuestState]):
                if node.is_leaf() and node != self.root_node:
                    all_leaves.append(node)
                for child in node.children:
                    collect_any_leaf(child)

            collect_any_leaf(self.root_node)

        if not all_leaves:
            self.final_response = "Failed to generate any valid responses."
            return

        # Sort by score
        all_leaves.sort(key=lambda n: n.score, reverse=True)
        top_leaves = all_leaves[:3]  # Top 3 responses

        # If only one good response, use it
        if len(top_leaves) == 1:
            self.final_response = top_leaves[0].state.text
            self.system_state.representative_agent_id = top_leaves[0].agent_id
        else:
            # Synthesize multiple responses
            # For now, we'll present the best one with acknowledgment of alternatives
            best_leaf = top_leaves[0]
            self.final_response = best_leaf.state.text

            # Add synthesis note if responses differ significantly
            if len(top_leaves) > 1:
                synthesis_note = "\n\n---\n[TreeQuest Synthesis: This response was selected as the most comprehensive from multiple high-quality candidates generated through adaptive tree search.]"
                self.final_response += synthesis_note

            self.system_state.representative_agent_id = best_leaf.agent_id

        # Update system state
        self.system_state.consensus_reached = True
        self.system_state.phase = "synthesis_complete"

        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("tree_search", "synthesis_complete")
            self.streaming_orchestrator.add_system_message(
                f"🎯 Synthesis complete! Selected response from Agent {self.system_state.representative_agent_id}"
            )

    def _finalize_session(self, session_duration: float) -> AlgorithmResult:
        """Finalize the session and return results."""
        logger.info("🏁 Finalizing TreeQuest session")

        self.system_state.end_time = time.time()

        # Collect tree statistics
        total_nodes = 0
        max_depth = 0

        def count_nodes(node: Node[TreeQuestState], depth: int):
            nonlocal total_nodes, max_depth
            total_nodes += 1
            max_depth = max(max_depth, depth)
            for child in node.children:
                count_nodes(child, depth + 1)

        if self.root_node:
            count_nodes(self.root_node, 0)

        # Prepare result
        result = AlgorithmResult(
            answer=self.final_response or "No final answer generated",
            consensus_reached=self.system_state.consensus_reached,
            representative_agent_id=self.system_state.representative_agent_id,
            session_duration=session_duration,
            summary={
                "total_agents": len(self.agents),
                "failed_agents": len([s for s in self.agent_states.values() if s.status == "failed"]),
                "algorithm": "treequest",
                "total_iterations": self.iteration_count,
                "tree_nodes": total_nodes,
                "tree_depth": max_depth,
                "best_score": self.best_leaves[0].score if self.best_leaves else 0.0,
            },
            algorithm_specific_data={
                "algorithm": "treequest",
                "implementation": "ab-mcts",
                "model_selection_strategy": self.model_selection_strategy,
                "iterations_completed": self.iteration_count,
                "tree_statistics": {
                    "total_nodes": total_nodes,
                    "max_depth": max_depth,
                    "leaf_nodes": len([n for n in self.best_leaves]),
                },
                "agent_performance": {
                    str(agent_id): {
                        "attempts": len(self.all_rewards_store.get(str(agent_id), [])),
                        "avg_score": np.mean(self.all_rewards_store.get(str(agent_id), [0])),
                        "max_score": max(self.all_rewards_store.get(str(agent_id), [0])),
                    }
                    for agent_id in self.agents
                },
            },
        )

        logger.info(f"✅ TreeQuest completed in {session_duration:.2f} seconds")
        logger.info(f"🌳 Tree statistics: {total_nodes} nodes, max depth {max_depth}")

        return result


# Register the algorithm
register_algorithm("treequest", TreeQuestAlgorithm)
