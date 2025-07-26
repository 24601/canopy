# Algorithm extensions for MassGen
# Based on the original MassGen framework: https://github.com/Leezekun/MassGen
"""
MassGen algorithm implementation.

This module implements the original MassGen consensus-based orchestration
algorithm where agents work together, share updates, and vote for the best solution.
"""

import logging
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from ..tracing import add_span_attributes, traced
from ..types import TaskInput, VoteRecord
from .base import AlgorithmResult, BaseAlgorithm
from .factory import register_algorithm

logger = logging.getLogger(__name__)


class MassGenAlgorithm(BaseAlgorithm):
    """MassGen consensus-based orchestration algorithm.

    This algorithm implements the original MassGen approach where:
    1. Agents work on task (status: "working")
    2. When agents vote, they become "voted"
    3. When all votable agents have voted:
       - Check consensus
       - If consensus reached: select representative to present final answer
       - If no consensus: restart all agents for debate
    4. Representative presents final answer and system completes
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
        """Initialize the MassGen algorithm."""
        super().__init__(agents, agent_states, system_state, config, log_manager, streaming_orchestrator)

        # Algorithm-specific configuration
        self.max_duration = config.get("max_duration", 600)
        self.consensus_threshold = config.get("consensus_threshold", 0.0)
        self.max_debate_rounds = config.get("max_debate_rounds", 1)
        self.status_check_interval = config.get("status_check_interval", 2.0)
        self.thread_pool_timeout = config.get("thread_pool_timeout", 5)

        # Internal state
        self.votes: List[VoteRecord] = []
        self.communication_log: List[Dict[str, Any]] = []
        self.final_response: Optional[str] = None

    def get_algorithm_name(self) -> str:
        """Return the algorithm name."""
        return "massgen"

    def validate_config(self) -> bool:
        """Validate the algorithm configuration."""
        if not 0.0 <= self.consensus_threshold <= 1.0:
            raise ValueError("Consensus threshold must be between 0.0 and 1.0")

        if self.max_duration <= 0:
            raise ValueError("Max duration must be positive")

        if self.max_debate_rounds < 0:
            raise ValueError("Max debate rounds must be non-negative")

        return True

    @traced("massgen_algorithm_run")
    def run(self, task: TaskInput) -> AlgorithmResult:
        """Run the MassGen consensus algorithm."""
        logger.info("🚀 Starting MassGen algorithm")

        add_span_attributes(
            {
                "algorithm.name": "massgen",
                "task.id": task.task_id,
                "agents.count": len(self.agents),
                "config.max_duration": self.max_duration,
                "config.consensus_threshold": self.consensus_threshold,
                "config.max_debate_rounds": self.max_debate_rounds,
            }
        )

        # Initialize algorithm state
        self._initialize_task(task)

        # Run the main workflow
        self._run_mass_workflow(task)

        # Finalize and return results
        return self._finalize_session()

    def cast_vote(self, voter_id: int, target_id: int, reason: str = "") -> None:
        """Record a vote from one agent for another agent's solution."""
        logger.info(f"🗳️ Agent {voter_id} casting vote for Agent {target_id}")

        if voter_id not in self.agent_states:
            raise ValueError(f"Voter agent {voter_id} not registered")
        if target_id not in self.agent_states:
            raise ValueError(f"Target agent {target_id} not registered")

        # Create vote record
        vote = VoteRecord(voter_id=voter_id, target_id=target_id, reason=reason, timestamp=time.time())

        # Record the vote
        self.votes.append(vote)

        # Update agent state
        old_status = self.agent_states[voter_id].status
        self.agent_states[voter_id].status = "voted"
        self.agent_states[voter_id].curr_vote = vote
        self.agent_states[voter_id].cast_votes.append(vote)
        self.agent_states[voter_id].execution_end_time = time.time()

        # Update streaming display
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_agent_status(voter_id, "voted")
            self.streaming_orchestrator.update_agent_vote_target(voter_id, target_id)
            vote_counts = self._get_current_vote_counts()
            self.streaming_orchestrator.update_vote_distribution(dict(vote_counts))
            vote_msg = f"👍 Agent {voter_id} voted for Agent {target_id}"
            self.streaming_orchestrator.add_system_message(vote_msg)

        # Log the vote
        if self.log_manager:
            self.log_manager.log_voting_event(
                voter_id=voter_id,
                target_id=target_id,
                phase=self.system_state.phase,
                reason=reason,
                orchestrator=self,
            )

    def notify_answer_update(self, agent_id: int, answer: str) -> None:
        """Called when an agent updates their answer."""
        logger.info(f"📢 Agent {agent_id} updated answer")

        # Update the answer
        self.update_agent_answer(agent_id, answer)

        # Update streaming display
        if self.streaming_orchestrator:
            answer_msg = f"📝 Agent {agent_id} updated answer ({len(answer)} chars)"
            self.streaming_orchestrator.add_system_message(answer_msg)
            update_count = len(self.agent_states[agent_id].updated_answers)
            self.streaming_orchestrator.update_agent_update_count(agent_id, update_count)

        # Restart voted agents when any agent shares new updates
        restarted_agents = []
        for other_agent_id, state in self.agent_states.items():
            if other_agent_id != agent_id and state.status == "voted":
                # Restart the voted agent
                state.status = "working"
                state.curr_vote = None
                state.execution_start_time = time.time()
                restarted_agents.append(other_agent_id)

                logger.info(f"🔄 Agent {other_agent_id} restarted due to update from Agent {agent_id}")

                # Update streaming display
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(other_agent_id, "working")
                    self.streaming_orchestrator.update_agent_vote_target(other_agent_id, None)
                    restart_msg = f"🔄 Agent {other_agent_id} restarted due to new update"
                    self.streaming_orchestrator.add_system_message(restart_msg)

                # Log agent restart
                if self.log_manager:
                    self.log_manager.log_agent_restart(
                        agent_id=other_agent_id,
                        reason=f"new_update_from_agent_{agent_id}",
                        phase=self.system_state.phase,
                    )

        if restarted_agents:
            logger.info(f"🔄 Restarted agents: {restarted_agents}")

            # Update vote distribution
            if self.streaming_orchestrator:
                vote_counts = self._get_current_vote_counts()
                self.streaming_orchestrator.update_vote_distribution(dict(vote_counts))

    def _initialize_task(self, task: TaskInput) -> None:
        """Initialize the system for a new task."""
        logger.info(f"🎯 Initializing MassGen algorithm for task: {task.task_id}")

        self.system_state.task = task
        self.system_state.start_time = time.time()
        self.system_state.phase = "collaboration"
        self.final_response = None

        # Reset all agent states
        for agent_id, agent in self.agents.items():
            from ..types import AgentState

            agent.state = AgentState(agent_id=agent_id)
            self.agent_states[agent_id] = agent.state
            agent.state.chat_history = []

            # Initialize streaming display for each agent
            if self.streaming_orchestrator:
                self.streaming_orchestrator.set_agent_model(agent_id, agent.model)
                self.streaming_orchestrator.update_agent_status(agent_id, "working")
                self.streaming_orchestrator.update_agent_update_count(agent_id, 0)

        # Clear previous session data
        self.votes.clear()
        self.communication_log.clear()

        # Initialize streaming display
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("unknown", "collaboration")
            self.streaming_orchestrator.update_debate_rounds(0)
            init_msg = f"🚀 Starting MassGen task with {len(self.agents)} agents"
            self.streaming_orchestrator.add_system_message(init_msg)

        self._log_event("task_started", {"task_id": task.task_id, "question": task.question})

    def _run_mass_workflow(self, task: TaskInput) -> None:
        """Run the MassGen workflow with dynamic agent restart support."""
        logger.info("🚀 Starting MassGen workflow")

        debate_rounds = 0
        start_time = time.time()

        while True:
            # Check timeout
            if time.time() - start_time > self.max_duration:
                logger.warning("⏰ Maximum duration reached - forcing consensus")
                self._force_consensus_by_timeout()
                self._present_final_answer(task)
                break

            # Run all agents with dynamic restart support
            logger.info(f"📢 Starting collaboration round {debate_rounds + 1}")
            self._run_all_agents_with_dynamic_restart(task)

            # Check if all votable agents have voted
            if self._all_agents_voted():
                logger.info("🗳️ All agents have voted - checking consensus")

                if self._check_consensus():
                    logger.info("🎉 Consensus reached!")
                    self._present_final_answer(task)
                    break
                else:
                    # No consensus - start debate round
                    debate_rounds += 1

                    if self.streaming_orchestrator:
                        self.streaming_orchestrator.update_debate_rounds(debate_rounds)

                    if debate_rounds > self.max_debate_rounds:
                        logger.warning(f"⚠️ Maximum debate rounds ({self.max_debate_rounds}) reached")
                        self._force_consensus_by_timeout()
                        self._present_final_answer(task)
                        break

                    logger.info(f"🗣️ No consensus - starting debate round {debate_rounds}")
                    self._restart_all_agents_for_debate()
            else:
                # Still waiting for some agents to vote
                time.sleep(self.status_check_interval)

    def _run_all_agents_with_dynamic_restart(self, task: TaskInput) -> None:
        """Run all agents in parallel with support for dynamic restarts."""
        active_futures = {}
        executor = ThreadPoolExecutor(max_workers=len(self.agents))

        try:
            # Start all working agents
            for agent_id in self.agents.keys():
                if self.agent_states[agent_id].status not in ["failed"]:
                    self._start_agent_if_working(agent_id, task, executor, active_futures)

            # Monitor agents and handle restarts
            while active_futures and not self._all_agents_voted():
                completed_futures = []

                # Check for completed agents
                for agent_id, future in list(active_futures.items()):
                    if future.done():
                        completed_futures.append(agent_id)
                        try:
                            future.result()  # Get result and handle exceptions
                        except Exception as e:
                            logger.error(f"❌ Agent {agent_id} failed: {e}")
                            self.mark_agent_failed(agent_id, str(e))

                # Remove completed futures
                for agent_id in completed_futures:
                    del active_futures[agent_id]

                # Check for agents that need to restart
                for agent_id in self.agents.keys():
                    if agent_id not in active_futures and self.agent_states[agent_id].status == "working":
                        self._start_agent_if_working(agent_id, task, executor, active_futures)

                time.sleep(0.1)  # Small delay to prevent busy waiting

        finally:
            # Cancel any remaining futures
            for future in active_futures.values():
                future.cancel()
            executor.shutdown(wait=True)

    def _start_agent_if_working(
        self, agent_id: int, task: TaskInput, executor: ThreadPoolExecutor, active_futures: Dict
    ) -> None:
        """Start an agent if it's in working status and not already running."""
        if self.agent_states[agent_id].status == "working" and agent_id not in active_futures:

            self.agent_states[agent_id].execution_start_time = time.time()
            future = executor.submit(self._run_single_agent, agent_id, task)
            active_futures[agent_id] = future
            logger.info(f"🤖 Agent {agent_id} started/restarted")

    def _run_single_agent(self, agent_id: int, task: TaskInput) -> None:
        """Run a single agent's work_on_task method."""
        agent = self.agents[agent_id]
        try:
            logger.info(f"🤖 Agent {agent_id} starting work")

            # Run agent's work_on_task with current conversation state
            updated_messages = agent.work_on_task(task)

            # Update conversation state
            self.agent_states[agent_id].chat_history.append(updated_messages)
            self.agent_states[agent_id].chat_round = agent.state.chat_round

            # Update streaming display with chat round
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_chat_round(agent_id, agent.state.chat_round)
                update_count = len(self.agent_states[agent_id].updated_answers)
                self.streaming_orchestrator.update_agent_update_count(agent_id, update_count)

            logger.info(f"✅ Agent {agent_id} completed work with status: {self.agent_states[agent_id].status}")

        except Exception as e:
            logger.error(f"❌ Agent {agent_id} failed: {e}")
            self.mark_agent_failed(agent_id, str(e))

    def _all_agents_voted(self) -> bool:
        """Check if all votable agents have voted."""
        votable_agents = [aid for aid, state in self.agent_states.items() if state.status not in ["failed"]]
        voted_agents = [aid for aid, state in self.agent_states.items() if state.status == "voted"]

        return len(voted_agents) == len(votable_agents) and len(votable_agents) > 0

    def _restart_all_agents_for_debate(self) -> None:
        """Restart all agents for debate by resetting their status."""
        logger.info("🔄 Restarting all agents for debate")

        # Update streaming display
        if self.streaming_orchestrator:
            self.streaming_orchestrator.reset_consensus()
            self.streaming_orchestrator.update_phase(self.system_state.phase, "collaboration")
            self.streaming_orchestrator.add_system_message("🗣️ Starting debate phase - no consensus reached")

        # Log debate start
        if self.log_manager:
            self.log_manager.log_debate_started(phase="collaboration")
            self.log_manager.log_phase_transition(
                old_phase=self.system_state.phase,
                new_phase="collaboration",
                additional_data={"reason": "no_consensus_reached", "debate_round": True},
            )

        # Reset agent statuses
        for agent_id, state in self.agent_states.items():
            if state.status not in ["failed"]:
                state.status = "working"

                # Update streaming display for each agent
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(agent_id, "working")

                # Log agent restart
                if self.log_manager:
                    self.log_manager.log_agent_restart(
                        agent_id=agent_id, reason="debate_phase_restart", phase="collaboration"
                    )

        # Update system phase
        self.system_state.phase = "collaboration"

    def _get_current_vote_counts(self) -> Counter:
        """Get current vote counts based on agent states' vote_target."""
        current_votes = []
        for agent_id, state in self.agent_states.items():
            if state.status == "voted" and state.curr_vote is not None:
                current_votes.append(state.curr_vote.target_id)

        # Create counter from actual votes
        vote_counts = Counter(current_votes)

        # Ensure all agents are represented (0 if no votes)
        for agent_id in self.agent_states.keys():
            if agent_id not in vote_counts:
                vote_counts[agent_id] = 0

        return vote_counts

    def _check_consensus(self) -> bool:
        """Check if consensus has been reached based on current votes."""
        total_agents = len(self.agents)
        failed_agents_count = len([s for s in self.agent_states.values() if s.status == "failed"])
        votable_agents_count = total_agents - failed_agents_count

        # Edge case: no votable agents
        if votable_agents_count == 0:
            logger.warning("⚠️ No votable agents available for consensus")
            return False

        # Edge case: only one votable agent
        if votable_agents_count == 1:
            working_agents = [aid for aid, state in self.agent_states.items() if state.status == "working"]
            if not working_agents:  # The single agent has voted
                votable_agent = [aid for aid, state in self.agent_states.items() if state.status != "failed"][0]
                logger.info(f"🎯 Single agent consensus: Agent {votable_agent}")
                self._reach_consensus(votable_agent)
                return True
            return False

        vote_counts = self._get_current_vote_counts()
        votes_needed = max(1, int(votable_agents_count * self.consensus_threshold))

        if vote_counts and vote_counts.most_common(1)[0][1] >= votes_needed:
            winning_agent_id = vote_counts.most_common(1)[0][0]
            winning_votes = vote_counts.most_common(1)[0][1]

            # Ensure the winning agent is still votable (not failed)
            if self.agent_states[winning_agent_id].status == "failed":
                logger.warning(f"⚠️ Winning agent {winning_agent_id} has failed - recalculating")
                return False

            logger.info(
                f"✅ Consensus reached: Agent {winning_agent_id} with {winning_votes}/{votable_agents_count} votes"
            )
            self._reach_consensus(winning_agent_id)
            return True

        return False

    def _reach_consensus(self, winning_agent_id: int) -> None:
        """Mark consensus as reached and finalize the system."""
        old_phase = self.system_state.phase
        self.system_state.consensus_reached = True
        self.system_state.representative_agent_id = winning_agent_id
        self.system_state.phase = "consensus"

        # Update streaming orchestrator if available
        if self.streaming_orchestrator:
            vote_distribution = dict(self._get_current_vote_counts())
            self.streaming_orchestrator.update_consensus_status(winning_agent_id, vote_distribution)
            self.streaming_orchestrator.update_phase(old_phase, "consensus")

        # Log to the comprehensive logging system
        if self.log_manager:
            vote_distribution = dict(self._get_current_vote_counts())
            self.log_manager.log_consensus_reached(
                winning_agent_id=winning_agent_id,
                vote_distribution=vote_distribution,
                is_fallback=False,
                phase=self.system_state.phase,
            )
            self.log_manager.log_phase_transition(
                old_phase=old_phase,
                new_phase="consensus",
                additional_data={
                    "consensus_reached": True,
                    "winning_agent_id": winning_agent_id,
                    "is_fallback": False,
                },
            )

        self._log_event(
            "consensus_reached",
            {
                "winning_agent_id": winning_agent_id,
                "fallback_to_majority": False,
                "final_vote_distribution": dict(self._get_current_vote_counts()),
            },
        )

    def _present_final_answer(self, task: TaskInput) -> None:
        """Run the final presentation by the representative agent."""
        representative_id = self.system_state.representative_agent_id
        if not representative_id:
            logger.error("No representative agent selected")
            return

        logger.info(f"🎯 Agent {representative_id} presenting final answer")

        try:
            representative_agent = self.agents[representative_id]

            # Run one more inference to generate the final answer
            _, user_input = representative_agent._get_task_input(task)

            messages = [
                {
                    "role": "system",
                    "content": """
You are given a task and multiple agents' answers and their votes.
Please incorporate these information and provide a final BEST answer to the original message.
""",
                },
                {
                    "role": "user",
                    "content": user_input
                    + """
Please provide the final BEST answer to the original message by incorporating these information.
The final answer must be self-contained, complete, well-sourced, compelling, and ready to serve as the definitive final response.
""",
                },
            ]
            result = representative_agent.process_message(messages)
            self.final_response = result.text

            # Mark completed
            self.system_state.phase = "completed"
            self.system_state.end_time = time.time()

            logger.info(f"✅ Final presentation completed by Agent {representative_id}")

        except Exception as e:
            logger.error(f"❌ Final presentation failed: {e}")
            self.final_response = f"Error in final presentation: {str(e)}"

    def _force_consensus_by_timeout(self) -> None:
        """Force consensus selection when maximum duration is reached."""
        logger.warning("⏰ Forcing consensus due to timeout")

        # Find agent with most votes, or earliest voter in case of tie
        vote_counts = self._get_current_vote_counts()

        if vote_counts:
            # Select agent with most votes
            winning_agent_id = vote_counts.most_common(1)[0][0]
            logger.info(f"   Selected Agent {winning_agent_id} with {vote_counts[winning_agent_id]} votes")
        else:
            # No votes - select first working agent
            working_agents = [aid for aid, state in self.agent_states.items() if state.status == "working"]
            winning_agent_id = working_agents[0] if working_agents else list(self.agents.keys())[0]
            logger.info(f"   No votes - selected Agent {winning_agent_id} as fallback")

        self._reach_consensus(winning_agent_id)

    def _finalize_session(self) -> AlgorithmResult:
        """Finalize the session and return comprehensive results."""
        logger.info("🏁 Finalizing MassGen session")

        if not self.system_state.end_time:
            self.system_state.end_time = time.time()

        session_duration = (
            self.system_state.end_time - self.system_state.start_time if self.system_state.start_time else 0
        )

        # Save final agent states to files
        if self.log_manager:
            self.log_manager.save_agent_states(self)
            self.log_manager.log_task_completion(
                {
                    "final_answer": self.final_response,
                    "consensus_reached": self.system_state.consensus_reached,
                    "representative_agent_id": self.system_state.representative_agent_id,
                    "session_duration": session_duration,
                }
            )

        # Prepare result
        result = AlgorithmResult(
            answer=self.final_response or "No final answer generated",
            consensus_reached=self.system_state.consensus_reached,
            representative_agent_id=self.system_state.representative_agent_id,
            session_duration=session_duration,
            summary={
                "total_agents": len(self.agents),
                "failed_agents": len([s for s in self.agent_states.values() if s.status == "failed"]),
                "total_votes": len(self.votes),
                "final_vote_distribution": dict(self._get_current_vote_counts()),
            },
            system_logs=self._export_detailed_session_log(),
            algorithm_specific_data={
                "debate_rounds": self.system_state.phase == "collaboration" and len(self.votes) > len(self.agents),
                "algorithm": "massgen",
            },
        )

        logger.info(f"✅ Session completed in {session_duration:.2f} seconds")
        logger.info(f"   Consensus: {result.consensus_reached}")
        logger.info(f"   Representative: Agent {result.representative_agent_id}")

        return result

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an orchestrator event."""
        self.communication_log.append({"timestamp": time.time(), "event_type": event_type, "data": data})

    def _export_detailed_session_log(self) -> Dict[str, Any]:
        """Export complete detailed session information."""
        from datetime import datetime

        session_log = {
            "session_metadata": {
                "session_id": (
                    f"mass_session_{int(self.system_state.start_time)}" if self.system_state.start_time else None
                ),
                "start_time": self.system_state.start_time,
                "end_time": self.system_state.end_time,
                "total_duration": (
                    (self.system_state.end_time - self.system_state.start_time)
                    if self.system_state.start_time and self.system_state.end_time
                    else None
                ),
                "timestamp": datetime.now().isoformat(),
                "system_version": "MassGen v1.0",
                "algorithm": "massgen",
            },
            "task_information": {
                "question": self.system_state.task.question if self.system_state.task else None,
                "task_id": self.system_state.task.task_id if self.system_state.task else None,
                "context": self.system_state.task.context if self.system_state.task else None,
            },
            "system_configuration": {
                "max_duration": self.max_duration,
                "consensus_threshold": self.consensus_threshold,
                "max_debate_rounds": self.max_debate_rounds,
                "agents": [agent.model for agent in self.agents.values()],
            },
            "agent_details": {
                agent_id: {
                    "status": state.status,
                    "updates_count": len(state.updated_answers),
                    "chat_length": len(state.chat_history),
                    "chat_round": state.chat_round,
                    "vote_target": state.curr_vote.target_id if state.curr_vote else None,
                    "execution_time": state.execution_time,
                    "execution_start_time": state.execution_start_time,
                    "execution_end_time": state.execution_end_time,
                    "updated_answers": [
                        {"timestamp": update.timestamp, "status": update.status, "answer_length": len(update.answer)}
                        for update in state.updated_answers
                    ],
                }
                for agent_id, state in self.agent_states.items()
            },
            "voting_analysis": {
                "vote_records": [
                    {
                        "voter_id": vote.voter_id,
                        "target_id": vote.target_id,
                        "timestamp": vote.timestamp,
                        "reason_length": len(vote.reason) if vote.reason else 0,
                    }
                    for vote in self.votes
                ],
                "vote_timeline": [
                    {"timestamp": vote.timestamp, "event": f"Agent {vote.voter_id} → Agent {vote.target_id}"}
                    for vote in self.votes
                ],
            },
            "communication_log": self.communication_log,
            "system_events": [
                {
                    "timestamp": entry["timestamp"],
                    "event_type": entry["event_type"],
                    "data_summary": {
                        k: (len(v) if isinstance(v, (str, list, dict)) else v) for k, v in entry["data"].items()
                    },
                }
                for entry in self.communication_log
            ],
        }

        return session_log


# Register the algorithm
register_algorithm("massgen", MassGenAlgorithm)
