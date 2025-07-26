"""
Default Algorithm Implementation

This is the original MassGen collaborative algorithm extracted from the
MassOrchestrator class. It implements the following workflow:

1. Agents work on task in parallel (status: "working")
2. When agents vote, they become "voted" 
3. When all votable agents have voted:
   - Check consensus
   - If consensus reached: select representative to present final answer
   - If no consensus: restart all agents for debate
4. Representative presents final answer and system completes

Key features:
- Dynamic agent restart when others share updates
- Consensus-based decision making
- Debate rounds for improved solutions
- Real-time collaboration through shared state
"""

import logging
import threading
import time
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List

from .base import Algorithm

logger = logging.getLogger(__name__)


class DefaultAlgorithm(Algorithm):
    """
    Default collaborative algorithm for MassGen.
    
    This algorithm maintains the original MassGen orchestration behavior
    where agents work in parallel, share updates, vote on solutions,
    and reach consensus through collaborative refinement.
    """
    
    def __init__(self, **kwargs):
        """Initialize the default algorithm."""
        super().__init__(**kwargs)
        
        # Algorithm-specific state
        self.votes: List[Any] = []  # Will be VoteRecord instances
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        
        # Initialize system state when imported types are available
        self._initialize_state()
    
    def _initialize_state(self):
        """Initialize system state when needed."""
        try:
            from ..types import SystemState
            if self.system_state is None:
                self.system_state = SystemState()
        except ImportError:
            # Create a simple state object if types aren't available
            class SimpleState:
                def __init__(self):
                    self.phase = "unknown"
                    self.consensus_reached = False
                    self.representative_agent_id = None
                    self.start_time = None
                    self.end_time = None
                    self.task = None
            self.system_state = SimpleState()
    
    def start_task(self, task) -> Dict[str, Any]:
        """
        Initialize the system for a new task and run the main workflow.
        
        Args:
            task: TaskInput containing the problem to solve
            
        Returns:
            Dict containing the final answer and relevant information
        """
        with self._lock:
            logger.info("🎯 ALGORITHM: Starting new task with Default algorithm")
            logger.info(f"   Task ID: {task.task_id}")
            logger.info(f"   Question preview: {task.question}")
            logger.info(f"   Registered agents: {list(self.agents.keys())}")
            logger.info(f"   Max duration: {self.max_duration}")
            logger.info(f"   Consensus threshold: {self.consensus_threshold}")

            self.system_state.task = task
            self.system_state.start_time = time.time()
            self.system_state.phase = "collaboration"
            self.final_response = None

            # Reset all agent states
            for agent_id, agent in self.agents.items():
                try:
                    from ..types import AgentState
                    agent.state = AgentState(agent_id=agent_id)
                except ImportError:
                    # Create simple agent state if types aren't available
                    class SimpleAgentState:
                        def __init__(self, agent_id):
                            self.agent_id = agent_id
                            self.status = "working"
                            self.chat_history = []
                            self.updated_answers = []
                            self.curr_answer = ""
                            self.curr_vote = None
                            self.cast_votes = []
                            self.chat_round = 0
                            self.execution_start_time = None
                            self.execution_end_time = None
                        
                        def add_update(self, answer):
                            self.curr_answer = answer
                    
                    agent.state = SimpleAgentState(agent_id)
                
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
            logger.info("✅ Task initialization completed successfully")
            
        # Run the workflow
        return self._run_algorithm_workflow(task)
    
    def _run_algorithm_workflow(self, task) -> Dict[str, Any]:
        """
        Execute the default collaborative algorithm workflow.
        
        Args:
            task: TaskInput containing the problem to solve
            
        Returns:
            Dict containing the final results
        """
        logger.info("🚀 Starting Default Algorithm workflow")
        
        debate_rounds = 0
        start_time = time.time()
        
        while not self._stop_event.is_set():
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
                
        return self._finalize_session()
    
    def cast_vote(self, voter_id: int, target_id: int, reason: str = ""):
        """
        Record a vote from one agent for another agent's solution.
        
        Args:
            voter_id: ID of the agent casting the vote
            target_id: ID of the agent being voted for
            reason: The reason for the vote (optional)
        """
        with self._lock:
            logger.info(f"🗳️ VOTING: Agent {voter_id} casting vote")

            print(f"🗳️  VOTE: Agent {voter_id} → Agent {target_id} ({self.system_state.phase})")
            if reason:
                print(f"   📝 Voting reason: {len(reason)} chars")

            if voter_id not in self.agent_states:
                logger.error(f"   ❌ Invalid voter: Agent {voter_id} not registered")
                raise ValueError(f"Voter agent {voter_id} not registered")
            if target_id not in self.agent_states:
                logger.error(f"   ❌ Invalid target: Agent {target_id} not registered")
                raise ValueError(f"Target agent {target_id} not registered")

            # Check current vote status
            previous_vote = self.agent_states[voter_id].curr_vote
            if previous_vote:
                logger.info(f"   🔄 Agent {voter_id} changed vote from Agent {previous_vote.target_id} to Agent {target_id}")
            else:
                logger.info(f"   ✨ Agent {voter_id} new vote for Agent {target_id}")

            # Add vote record
            try:
                from ..types import VoteRecord
                vote = VoteRecord(voter_id=voter_id, 
                                  target_id=target_id, 
                                  reason=reason,
                                  timestamp=time.time())
            except ImportError:
                # Create simple vote record if types aren't available
                class SimpleVoteRecord:
                    def __init__(self, voter_id, target_id, reason, timestamp):
                        self.voter_id = voter_id
                        self.target_id = target_id
                        self.reason = reason
                        self.timestamp = timestamp
                
                vote = SimpleVoteRecord(voter_id, target_id, reason, time.time())
            
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
                update_count = len(self.agent_states[voter_id].updated_answers)
                self.streaming_orchestrator.update_agent_update_count(voter_id, update_count)
                
                for agent_id, agent_state in self.agent_states.items():
                    vote_cast_count = len(agent_state.cast_votes)
                    self.streaming_orchestrator.update_agent_votes_cast(agent_id, vote_cast_count)
                
                vote_counts = self._get_current_vote_counts()
                self.streaming_orchestrator.update_vote_distribution(dict(vote_counts))
                vote_msg = f"👍 Agent {voter_id} voted for Agent {target_id}"
                self.streaming_orchestrator.add_system_message(vote_msg)

            # Log to the comprehensive logging system
            if self.log_manager:
                self.log_manager.log_voting_event(
                    voter_id=voter_id,
                    target_id=target_id,
                    phase=self.system_state.phase,
                    reason=reason,
                    orchestrator=self
                )
                self.log_manager.log_agent_status_change(
                    agent_id=voter_id,
                    old_status=old_status,
                    new_status="voted",
                    phase=self.system_state.phase
                )

            # Show current vote distribution
            vote_counts = self._get_current_vote_counts()
            voted_agents_count = self._get_current_voted_agents_count()
            logger.info(f"   📊 Vote distribution: {dict(vote_counts)}")
            logger.info(f"   📈 Voting progress: {voted_agents_count}/{len(self.agent_states)} agents voted")

            # Calculate consensus requirements
            total_agents = len(self.agent_states)
            votes_needed = max(1, int(total_agents * self.consensus_threshold))
            if vote_counts:
                leading_agent, leading_votes = vote_counts.most_common(1)[0]
                logger.info(
                    f"   🏆 Leading: Agent {leading_agent} with {leading_votes} votes (need {votes_needed} for consensus)"
                )

            # Log event for internal tracking
            self._log_event(
                "vote_cast",
                {
                    "voter_id": voter_id,
                    "target_id": target_id,
                    "timestamp": vote.timestamp,
                    "vote_distribution": dict(vote_counts),
                    "total_votes": voted_agents_count,
                },
            )
    
    def update_agent_answer(self, agent_id: int, answer: str):
        """
        Update an agent's answer and restart voted agents.
        
        Args:
            agent_id: ID of the agent updating their answer
            answer: New answer content
        """
        logger.info(f"📢 Agent {agent_id} updated answer")
        
        # Update the answer in agent state
        super().update_agent_answer(agent_id, answer)
        
        old_answer_length = len(self.agent_states[agent_id].curr_answer)
        preview = answer[:100] + "..." if len(answer) > 100 else answer
        print(f"📝 Agent {agent_id} answer updated ({old_answer_length} → {len(answer)} chars)")
        print(f"   🔍 {preview}")
        
        # Update streaming display
        if self.streaming_orchestrator:
            answer_msg = f"📝 Agent {agent_id} updated answer ({len(answer)} chars)"
            self.streaming_orchestrator.add_system_message(answer_msg)
            update_count = len(self.agent_states[agent_id].updated_answers)
            self.streaming_orchestrator.update_agent_update_count(agent_id, update_count)
        
        # Restart voted agents when any agent shares new updates
        with self._lock:
            restarted_agents = []
            
            for other_agent_id, state in self.agent_states.items():
                if (other_agent_id != agent_id and 
                    state.status == "voted"):
                    
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
                        update_count = len(self.agent_states[other_agent_id].updated_answers)
                        self.streaming_orchestrator.update_agent_update_count(other_agent_id, update_count)
                        restart_msg = f"🔄 Agent {other_agent_id} restarted due to new update"
                        self.streaming_orchestrator.add_system_message(restart_msg)
                    
                    # Log agent restart
                    if self.log_manager:
                        self.log_manager.log_agent_restart(
                            agent_id=other_agent_id,
                            reason=f"new_update_from_agent_{agent_id}",
                            phase=self.system_state.phase
                        )
            
            if restarted_agents:
                logger.info(f"🔄 Restarted agents: {restarted_agents}")
                
                # Update vote distribution in streaming display
                if self.streaming_orchestrator:
                    vote_counts = self._get_current_vote_counts()
                    self.streaming_orchestrator.update_vote_distribution(dict(vote_counts))
                    for agent_id, agent_state in self.agent_states.items():
                        vote_cast_count = len(agent_state.cast_votes)
                        self.streaming_orchestrator.update_agent_votes_cast(agent_id, vote_cast_count)
            
            return restarted_agents
    
    def _get_current_vote_counts(self) -> Counter:
        """Get current vote counts based on agent states' vote_target."""
        current_votes = []
        for agent_id, state in self.agent_states.items():
            if state.status == "voted" and state.curr_vote is not None:
                current_votes.append(state.curr_vote.target_id)
        
        vote_counts = Counter(current_votes)
        
        # Ensure all agents are represented (0 if no votes)
        for agent_id in self.agent_states.keys():
            if agent_id not in vote_counts:
                vote_counts[agent_id] = 0
                
        return vote_counts
    
    def _get_current_voted_agents_count(self) -> int:
        """Get count of agents who currently have status "voted"."""
        return len([s for s in self.agent_states.values() if s.status == "voted"])
    
    def _check_consensus(self) -> bool:
        """Check if consensus has been reached based on current votes."""
        with self._lock:
            total_agents = len(self.agents)
            failed_agents_count = len([s for s in self.agent_states.values() if s.status == "failed"])
            votable_agents_count = total_agents - failed_agents_count
            
            if votable_agents_count == 0:
                logger.warning("⚠️ No votable agents available for consensus")
                return False
            
            if votable_agents_count == 1:
                working_agents = [aid for aid, state in self.agent_states.items() 
                                if state.status == "working"]
                if not working_agents:
                    votable_agent = [aid for aid, state in self.agent_states.items() 
                                   if state.status != "failed"][0]
                    logger.info(f"🎯 Single agent consensus: Agent {votable_agent}")
                    self._reach_consensus(votable_agent)
                    return True
                return False
                
            vote_counts = self._get_current_vote_counts()
            votes_needed = max(1, int(votable_agents_count * self.consensus_threshold))
            
            if vote_counts and vote_counts.most_common(1)[0][1] >= votes_needed:
                winning_agent_id = vote_counts.most_common(1)[0][0]
                winning_votes = vote_counts.most_common(1)[0][1]
                
                if self.agent_states[winning_agent_id].status == "failed":
                    logger.warning(f"⚠️ Winning agent {winning_agent_id} has failed - recalculating")
                    return False
                    
                logger.info(f"✅ Consensus reached: Agent {winning_agent_id} with {winning_votes}/{votable_agents_count} votes")
                self._reach_consensus(winning_agent_id)
                return True
                
            return False
    
    def _reach_consensus(self, winning_agent_id: int):
        """Mark consensus as reached and finalize the system."""
        old_phase = self.system_state.phase
        self.system_state.consensus_reached = True
        self.system_state.representative_agent_id = winning_agent_id
        self.system_state.phase = "consensus"

        if self.streaming_orchestrator:
            vote_distribution = dict(self._get_current_vote_counts())
            self.streaming_orchestrator.update_consensus_status(winning_agent_id, vote_distribution)
            self.streaming_orchestrator.update_phase(old_phase, "consensus")

        if self.log_manager:
            vote_distribution = dict(self._get_current_vote_counts())
            self.log_manager.log_consensus_reached(
                winning_agent_id=winning_agent_id,
                vote_distribution=vote_distribution,
                is_fallback=False,
                phase=self.system_state.phase
            )
            self.log_manager.log_phase_transition(
                old_phase=old_phase,
                new_phase="consensus",
                additional_data={
                    "consensus_reached": True,
                    "winning_agent_id": winning_agent_id,
                    "is_fallback": False,
                }
            )

        self._log_event(
            "consensus_reached",
            {
                "winning_agent_id": winning_agent_id,
                "fallback_to_majority": False,
                "final_vote_distribution": dict(self._get_current_vote_counts()),
            }
        )
    
    def _run_all_agents_with_dynamic_restart(self, task):
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
                            future.result()
                        except Exception as e:
                            logger.error(f"❌ Agent {agent_id} failed: {e}")
                            self.mark_agent_failed(agent_id, str(e))
                
                # Remove completed futures
                for agent_id in completed_futures:
                    del active_futures[agent_id]
                
                # Check for agents that need to restart
                for agent_id in self.agents.keys():
                    if (agent_id not in active_futures and 
                        self.agent_states[agent_id].status == "working"):
                        self._start_agent_if_working(agent_id, task, executor, active_futures)
                
                time.sleep(0.1)
                
        finally:
            for future in active_futures.values():
                future.cancel()
            executor.shutdown(wait=True)
    
    def _start_agent_if_working(self, agent_id: int, task, executor: ThreadPoolExecutor, active_futures: Dict):
        """Start an agent if it's in working status and not already running."""
        if (self.agent_states[agent_id].status == "working" and 
            agent_id not in active_futures):
            
            self.agent_states[agent_id].execution_start_time = time.time()
            future = executor.submit(self._run_single_agent, agent_id, task)
            active_futures[agent_id] = future
            logger.info(f"🤖 Agent {agent_id} started/restarted")
    
    def _run_single_agent(self, agent_id: int, task):
        """Run a single agent's work_on_task method."""
        agent = self.agents[agent_id]
        try:
            logger.info(f"🤖 Agent {agent_id} starting work")
    
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
        votable_agents = [aid for aid, state in self.agent_states.items() 
                         if state.status not in ["failed"]]
        voted_agents = [aid for aid, state in self.agent_states.items() 
                       if state.status == "voted"]
        
        return len(voted_agents) == len(votable_agents) and len(votable_agents) > 0
    
    def _restart_all_agents_for_debate(self):
        """Restart all agents for debate by resetting their status."""
        logger.info("🔄 Restarting all agents for debate")
        
        with self._lock:
            if self.streaming_orchestrator:
                self.streaming_orchestrator.reset_consensus()
                self.streaming_orchestrator.update_phase(self.system_state.phase, "collaboration")
                self.streaming_orchestrator.add_system_message("🗣️ Starting debate phase - no consensus reached")
            
            if self.log_manager:
                self.log_manager.log_debate_started(phase="collaboration")
                self.log_manager.log_phase_transition(
                    old_phase=self.system_state.phase,
                    new_phase="collaboration",
                    additional_data={"reason": "no_consensus_reached", "debate_round": True}
                )
            
            # Reset agent statuses for debate
            for agent_id, state in self.agent_states.items():
                if state.status not in ["failed"]:
                    old_status = state.status
                    state.status = "working"
                    
                    if self.streaming_orchestrator:
                        self.streaming_orchestrator.update_agent_status(agent_id, "working")

                    if self.log_manager:
                        self.log_manager.log_agent_restart(
                            agent_id=agent_id,
                            reason="debate_phase_restart",
                            phase="collaboration"
                        )
            
            self.system_state.phase = "collaboration"
    
    def _present_final_answer(self, task):
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
                {"role": "system", "content": """
You are given a task and multiple agents' answers and their votes. 
Please incorporate these information and provide a final BEST answer to the original message.
"""},
                {"role": "user", "content": user_input + """
Please provide the final BEST answer to the original message by incorporating these information.
The final answer must be self-contained, complete, well-sourced, compelling, and ready to serve as the definitive final response.
"""}
            ]
            result = representative_agent.process_message(messages)
            self.final_response = result.text
            
            self.system_state.phase = "completed"
            self.system_state.end_time = time.time()
            
            logger.info(f"✅ Final presentation completed by Agent {representative_id}")
            
        except Exception as e:
            logger.error(f"❌ Final presentation failed: {e}")
            self.final_response = f"Error in final presentation: {str(e)}"
    
    def _force_consensus_by_timeout(self):
        """Force consensus selection when maximum duration is reached."""
        logger.warning("⏰ Forcing consensus due to timeout")
        
        with self._lock:
            vote_counts = self._get_current_vote_counts()
            
            if vote_counts:
                winning_agent_id = vote_counts.most_common(1)[0][0]
                logger.info(f"   Selected Agent {winning_agent_id} with {vote_counts[winning_agent_id]} votes")
            else:
                working_agents = [aid for aid, state in self.agent_states.items() 
                                if state.status == "working"]
                winning_agent_id = working_agents[0] if working_agents else list(self.agents.keys())[0]
                logger.info(f"   No votes - selected Agent {winning_agent_id} as fallback")
                
            self._reach_consensus(winning_agent_id)
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an orchestrator event."""
        self.communication_log.append({"timestamp": time.time(), "event_type": event_type, "data": data})
    
    def _finalize_session(self) -> Dict[str, Any]:
        """Finalize the session with algorithm-specific results."""
        result = super()._finalize_session()
        
        # Add default algorithm specific data
        result["summary"].update({
            "total_votes": len(self.votes),
            "final_vote_distribution": dict(self._get_current_vote_counts()),
        })
        
        # Save detailed session log
        result["system_logs"] = self._export_detailed_session_log()
        
        # Save result to result.json
        if self.log_manager and not self.log_manager.non_blocking:
            try:
                result_file = self.log_manager.session_dir / "result.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"💾 Result saved to {result_file}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to save result.json: {e}")
        
        return result
    
    def _export_detailed_session_log(self) -> Dict[str, Any]:
        """Export complete detailed session information."""
        from datetime import datetime
        
        session_log = {
            "session_metadata": {
                "session_id": f"mass_session_{int(self.system_state.start_time)}"
                if self.system_state.start_time else None,
                "start_time": self.system_state.start_time,
                "end_time": self.system_state.end_time,
                "total_duration": (self.system_state.end_time - self.system_state.start_time)
                if self.system_state.start_time and self.system_state.end_time else None,
                "timestamp": datetime.now().isoformat(),
                "system_version": "MassGen v1.0",
                "algorithm": "DefaultAlgorithm"
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
            },
            "communication_log": self.communication_log,
        }

        return session_log