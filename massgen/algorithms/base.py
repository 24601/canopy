"""
Base Algorithm Interface

This module defines the abstract base class that all multi-agent orchestration
algorithms must implement. It provides a standard interface for different
orchestration strategies while allowing the rest of the system (agents, 
streaming display, logging) to remain unchanged.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class Algorithm(ABC):
    """
    Abstract base class for multi-agent orchestration algorithms.
    
    All algorithms must implement this interface to be compatible with the
    MassGen system. The interface provides hooks for:
    - Task initialization and execution
    - Agent management and coordination
    - Result finalization and cleanup
    """
    
    def __init__(
        self,
        max_duration: int = 600,
        consensus_threshold: float = 0.0,
        max_debate_rounds: int = 1,
        status_check_interval: float = 2.0,
        thread_pool_timeout: int = 5,
        streaming_orchestrator=None,
        **kwargs
    ):
        """
        Initialize the algorithm with common parameters.
        
        Args:
            max_duration: Maximum duration for the entire task in seconds
            consensus_threshold: Fraction of agents that must agree for consensus
            max_debate_rounds: Maximum number of debate rounds before fallback
            status_check_interval: Interval for checking agent status (seconds)
            thread_pool_timeout: Timeout for shutting down thread pool executor
            streaming_orchestrator: Optional streaming orchestrator for real-time display
            **kwargs: Algorithm-specific parameters
        """
        self.max_duration = max_duration
        self.consensus_threshold = consensus_threshold
        self.max_debate_rounds = max_debate_rounds
        self.status_check_interval = status_check_interval
        self.thread_pool_timeout = thread_pool_timeout
        self.streaming_orchestrator = streaming_orchestrator
        
        # Common state management
        self.agents: Dict[int, Any] = {}
        self.agent_states: Dict[int, Any] = {}  # Will be AgentState instances
        self.system_state = None  # Will be SystemState instance
        
        # Communication and logging
        self.communication_log: List[Dict[str, Any]] = []
        self.final_response: Optional[str] = None
        self.log_manager = None
    
    def register_agent(self, agent):
        """
        Register an agent with the algorithm.
        
        Args:
            agent: MassAgent instance to register
        """
        self.agents[agent.agent_id] = agent
        self.agent_states[agent.agent_id] = agent.state
        agent.orchestrator = self  # Set back-reference for agent
    
    @abstractmethod
    def start_task(self, task) -> Dict[str, Any]:
        """
        Initialize and execute the algorithm for a given task.
        
        Args:
            task: TaskInput containing the problem to solve
            
        Returns:
            Dict containing the final answer and metadata
        """
        pass
    
    @abstractmethod
    def _run_algorithm_workflow(self, task) -> Dict[str, Any]:
        """
        Execute the core algorithm workflow.
        
        This is where each algorithm implements its specific orchestration strategy.
        
        Args:
            task: TaskInput containing the problem to solve
            
        Returns:
            Dict containing the final results
        """
        pass
    
    def update_agent_answer(self, agent_id: int, answer: str):
        """
        Update an agent's running answer.
        
        This method can be overridden by algorithms that want custom
        handling of agent answer updates.
        
        Args:
            agent_id: ID of the agent updating their answer
            answer: New answer content
        """
        if agent_id not in self.agent_states:
            raise ValueError(f"Agent {agent_id} not registered")
        
        # Call add_update method if available
        if hasattr(self.agent_states[agent_id], 'add_update'):
            self.agent_states[agent_id].add_update(answer)
        
        if self.log_manager and hasattr(self.log_manager, 'log_agent_answer_update'):
            phase = getattr(self.system_state, 'phase', 'unknown') if self.system_state else 'unknown'
            self.log_manager.log_agent_answer_update(
                agent_id=agent_id,
                answer=answer,
                phase=phase,
                orchestrator=self
            )
    
    def cast_vote(self, voter_id: int, target_id: int, reason: str = ""):
        """
        Record a vote from one agent for another agent's solution.
        
        Default implementation - can be overridden by algorithms.
        
        Args:
            voter_id: ID of the agent casting the vote
            target_id: ID of the agent being voted for
            reason: The reason for the vote (optional)
        """
        raise NotImplementedError("Voting not implemented for this algorithm")
    
    def mark_agent_failed(self, agent_id: int, reason: str = ""):
        """
        Mark an agent as failed.
        
        Args:
            agent_id: ID of the agent to mark as failed
            reason: Optional reason for the failure
        """
        if agent_id not in self.agent_states:
            raise ValueError(f"Agent {agent_id} not registered")
        
        old_status = getattr(self.agent_states[agent_id], 'status', 'unknown')
        if hasattr(self.agent_states[agent_id], 'status'):
            self.agent_states[agent_id].status = "failed"
        if hasattr(self.agent_states[agent_id], 'execution_end_time'):
            self.agent_states[agent_id].execution_end_time = time.time()
        
        logger.info(f"💥 Agent {agent_id} marked as failed: {reason}")
        
        if self.streaming_orchestrator and hasattr(self.streaming_orchestrator, 'update_agent_status'):
            self.streaming_orchestrator.update_agent_status(agent_id, "failed")
            failure_msg = f"💥 Agent {agent_id} failed: {reason}" if reason else f"💥 Agent {agent_id} failed"
            if hasattr(self.streaming_orchestrator, 'add_system_message'):
                self.streaming_orchestrator.add_system_message(failure_msg)
        
        if self.log_manager and hasattr(self.log_manager, 'log_agent_status_change'):
            phase = getattr(self.system_state, 'phase', 'unknown') if self.system_state else 'unknown'
            self.log_manager.log_agent_status_change(
                agent_id=agent_id,
                old_status=old_status,
                new_status="failed",
                phase=phase
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status information."""
        return {
            "phase": getattr(self.system_state, 'phase', 'unknown') if self.system_state else 'unknown',
            "consensus_reached": getattr(self.system_state, 'consensus_reached', False) if self.system_state else False,
            "agents": {
                agent_id: {
                    "status": getattr(state, 'status', 'unknown'),
                    "update_times": len(getattr(state, 'updated_answers', [])),
                    "chat_round": getattr(state, 'chat_round', 0),
                    "execution_time": getattr(state, 'execution_time', None),
                }
                for agent_id, state in self.agent_states.items()
            },
            "runtime": (time.time() - getattr(self.system_state, 'start_time', time.time())) if self.system_state and hasattr(self.system_state, 'start_time') else 0,
        }
    
    def _finalize_session(self) -> Dict[str, Any]:
        """
        Finalize the session and return comprehensive results.
        
        Common finalization logic that can be used by all algorithms.
        """
        logger.info("🏁 Finalizing session")
        
        # Set end time if not set
        if self.system_state and not getattr(self.system_state, 'end_time', None):
            self.system_state.end_time = time.time()
        
        start_time = getattr(self.system_state, 'start_time', None) if self.system_state else None
        end_time = getattr(self.system_state, 'end_time', time.time()) if self.system_state else time.time()
        session_duration = (end_time - start_time) if start_time else 0
        
        # Save final agent states
        if self.log_manager and hasattr(self.log_manager, 'save_agent_states'):
            self.log_manager.save_agent_states(self)
            if hasattr(self.log_manager, 'log_task_completion'):
                self.log_manager.log_task_completion({
                    "final_answer": self.final_response,
                    "consensus_reached": getattr(self.system_state, 'consensus_reached', False) if self.system_state else False,
                    "representative_agent_id": getattr(self.system_state, 'representative_agent_id', None) if self.system_state else None,
                    "session_duration": session_duration
                })
        
        # Prepare result
        result = {
            "answer": self.final_response or "No final answer generated",
            "consensus_reached": getattr(self.system_state, 'consensus_reached', False) if self.system_state else False,
            "representative_agent_id": getattr(self.system_state, 'representative_agent_id', None) if self.system_state else None,
            "session_duration": session_duration,
            "algorithm": self.__class__.__name__,
            "summary": {
                "total_agents": len(self.agents),
                "failed_agents": len([s for s in self.agent_states.values() if getattr(s, 'status', None) == "failed"]),
            }
        }
        
        logger.info(f"✅ Session completed in {session_duration:.2f} seconds")
        logger.info(f"   Algorithm: {result['algorithm']}")
        logger.info(f"   Consensus: {result['consensus_reached']}")
        logger.info(f"   Representative: Agent {result['representative_agent_id']}")
        
        return result
    
    def cleanup(self):
        """
        Clean up resources and stop all agents.
        
        Common cleanup logic that can be used by all algorithms.
        """
        logger.info("🧹 Cleaning up algorithm resources")
        
        # Save final agent states before cleanup
        if self.log_manager and self.agent_states and hasattr(self.log_manager, 'save_agent_states'):
            try:
                self.log_manager.save_agent_states(self)
                logger.info("✅ Final agent states saved")
            except Exception as e:
                logger.warning(f"⚠️ Error saving final agent states: {e}")
        
        # Clean up logging manager
        if self.log_manager and hasattr(self.log_manager, 'cleanup'):
            try:
                self.log_manager.cleanup()
                logger.info("✅ Log manager cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning up log manager: {e}")
        
        # Clean up streaming orchestrator
        if self.streaming_orchestrator and hasattr(self.streaming_orchestrator, 'cleanup'):
            try:
                self.streaming_orchestrator.cleanup()
                logger.info("✅ Streaming orchestrator cleaned up")
            except Exception as e:
                logger.warning(f"⚠️ Error cleaning up streaming orchestrator: {e}")
        
        logger.info("✅ Algorithm cleanup completed")