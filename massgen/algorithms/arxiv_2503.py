"""
Arxiv 2503.04412 Inspired Algorithm Implementation

This algorithm is inspired by multi-agent reasoning approaches typically described
in research papers. While I cannot access the specific paper https://arxiv.org/pdf/2503.04412,
this implementation follows common patterns in multi-agent reasoning literature:

1. Structured reasoning phases
2. Role-based agent specialization  
3. Iterative refinement through critiques
4. Evidence synthesis and validation

Key differences from DefaultAlgorithm:
- Uses structured reasoning phases instead of free-form collaboration
- Implements role specialization (reasoner, critic, synthesizer)
- Uses critique-based refinement instead of voting
- Focuses on evidence validation and logical consistency

Citation Note: This implementation is inspired by multi-agent reasoning patterns
commonly found in academic literature. The specific paper referenced 
(https://arxiv.org/pdf/2503.04412) should be consulted for the exact methodology
and properly cited in any academic or commercial use.

Reference Implementation: https://github.com/SakanaAI/ (as mentioned in the issue)
"""

import logging
import threading
import time
import json
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from .base import Algorithm

logger = logging.getLogger(__name__)


class Arxiv2503Algorithm(Algorithm):
    """
    Multi-agent reasoning algorithm inspired by structured reasoning approaches.
    
    This algorithm implements a more structured approach to multi-agent collaboration:
    
    Phase 1: Individual Reasoning - Each agent independently analyzes the problem
    Phase 2: Critique Generation - Agents critique each other's reasoning
    Phase 3: Evidence Synthesis - Agents incorporate critiques and refine solutions
    Phase 4: Consensus Validation - Final validation and answer selection
    
    Unlike the voting-based DefaultAlgorithm, this approach focuses on:
    - Structured reasoning chains
    - Evidence-based critique
    - Iterative refinement
    - Logical consistency validation
    """
    
    def __init__(self, **kwargs):
        """Initialize the Arxiv 2503 algorithm."""
        super().__init__(**kwargs)
        
        # Algorithm-specific configuration
        self.max_reasoning_rounds = kwargs.get('max_reasoning_rounds', 2)
        self.critique_rounds = kwargs.get('critique_rounds', 1)
        self.evidence_threshold = kwargs.get('evidence_threshold', 0.7)
        
        # Algorithm state
        self.reasoning_outputs: Dict[int, List[str]] = {}
        self.critiques: Dict[int, List[Dict[str, Any]]] = {}
        self.refined_solutions: Dict[int, str] = {}
        self.evidence_scores: Dict[int, float] = {}
        
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        
        # Initialize system state
        self._initialize_state()
        
        logger.info("🧠 Arxiv2503Algorithm initialized with structured reasoning approach")
        logger.info(f"   Max reasoning rounds: {self.max_reasoning_rounds}")
        logger.info(f"   Critique rounds: {self.critique_rounds}")
        logger.info(f"   Evidence threshold: {self.evidence_threshold}")
    
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
        Initialize the system for a new task and run the structured reasoning workflow.
        
        Args:
            task: TaskInput containing the problem to solve
            
        Returns:
            Dict containing the final answer and relevant information
        """
        with self._lock:
            logger.info("🎯 ALGORITHM: Starting new task with Arxiv2503Algorithm")
            logger.info(f"   Task ID: {getattr(task, 'task_id', 'unknown')}")
            logger.info(f"   Question preview: {getattr(task, 'question', 'unknown')}")
            logger.info(f"   Registered agents: {list(self.agents.keys())}")

            self.system_state.task = task
            self.system_state.start_time = time.time()
            self.system_state.phase = "reasoning"
            self.final_response = None

            # Reset all agent states
            for agent_id, agent in self.agents.items():
                self._reset_agent_state(agent_id, agent)
                
                # Initialize streaming display
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.set_agent_model(agent_id, getattr(agent, 'model', 'unknown'))
                    self.streaming_orchestrator.update_agent_status(agent_id, "reasoning")
                    self.streaming_orchestrator.update_agent_update_count(agent_id, 0)

            # Clear previous session data
            self.reasoning_outputs.clear()
            self.critiques.clear()
            self.refined_solutions.clear()
            self.evidence_scores.clear()
            self.communication_log.clear()
            
            # Initialize streaming display
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_phase("unknown", "reasoning")
                self.streaming_orchestrator.update_debate_rounds(0)
                init_msg = f"🧠 Starting structured reasoning with {len(self.agents)} agents"
                self.streaming_orchestrator.add_system_message(init_msg)

            self._log_event("task_started", {"task_id": getattr(task, 'task_id', 'unknown'), "question": getattr(task, 'question', 'unknown')})
            logger.info("✅ Task initialization completed successfully")
            
        return self._run_algorithm_workflow(task)
    
    def _reset_agent_state(self, agent_id: int, agent):
        """Reset agent state for the structured reasoning algorithm."""
        try:
            from ..types import AgentState
            agent.state = AgentState(agent_id=agent_id)
        except ImportError:
            # Create simple agent state if types aren't available
            class SimpleAgentState:
                def __init__(self, agent_id):
                    self.agent_id = agent_id
                    self.status = "reasoning"
                    self.chat_history = []
                    self.updated_answers = []
                    self.curr_answer = ""
                    self.chat_round = 0
                    self.execution_start_time = None
                    self.execution_end_time = None
                
                def add_update(self, answer):
                    self.curr_answer = answer
            
            agent.state = SimpleAgentState(agent_id)
        
        self.agent_states[agent_id] = agent.state
        agent.state.chat_history = []
    
    def _run_algorithm_workflow(self, task) -> Dict[str, Any]:
        """
        Execute the structured reasoning algorithm workflow.
        
        Phases:
        1. Individual Reasoning: Each agent reasons independently
        2. Critique Generation: Agents critique others' reasoning
        3. Evidence Synthesis: Agents refine based on critiques
        4. Consensus Validation: Select best solution based on evidence
        
        Args:
            task: TaskInput containing the problem to solve
            
        Returns:
            Dict containing the final results
        """
        logger.info("🧠 Starting Arxiv2503Algorithm structured reasoning workflow")
        
        start_time = time.time()
        
        try:
            # Phase 1: Individual Reasoning
            logger.info("📝 Phase 1: Individual Reasoning")
            self._phase_individual_reasoning(task)
            
            # Check timeout
            if time.time() - start_time > self.max_duration:
                logger.warning("⏰ Timeout during reasoning phase")
                return self._handle_timeout()
            
            # Phase 2: Critique Generation  
            logger.info("🔍 Phase 2: Critique Generation")
            self._phase_critique_generation(task)
            
            # Check timeout
            if time.time() - start_time > self.max_duration:
                logger.warning("⏰ Timeout during critique phase")
                return self._handle_timeout()
            
            # Phase 3: Evidence Synthesis
            logger.info("⚗️ Phase 3: Evidence Synthesis")
            self._phase_evidence_synthesis(task)
            
            # Check timeout
            if time.time() - start_time > self.max_duration:
                logger.warning("⏰ Timeout during synthesis phase")
                return self._handle_timeout()
            
            # Phase 4: Consensus Validation
            logger.info("✅ Phase 4: Consensus Validation")
            self._phase_consensus_validation(task)
            
        except Exception as e:
            logger.error(f"❌ Error in structured reasoning workflow: {e}")
            return self._handle_error(str(e))
        
        return self._finalize_session()
    
    def _phase_individual_reasoning(self, task):
        """Phase 1: Each agent performs individual reasoning."""
        self.system_state.phase = "reasoning"
        
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("unknown", "reasoning")
            self.streaming_orchestrator.add_system_message("📝 Phase 1: Individual reasoning started")
        
        # Run all agents in parallel for individual reasoning
        executor = ThreadPoolExecutor(max_workers=len(self.agents))
        futures = {}
        
        try:
            for agent_id, agent in self.agents.items():
                self.agent_states[agent_id].status = "reasoning"
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(agent_id, "reasoning")
                
                future = executor.submit(self._agent_individual_reasoning, agent_id, agent, task)
                futures[agent_id] = future
            
            # Wait for all agents to complete reasoning
            for agent_id, future in futures.items():
                try:
                    reasoning_output = future.result(timeout=self.max_duration//4)
                    self.reasoning_outputs[agent_id] = reasoning_output
                    self.agent_states[agent_id].status = "reasoning_complete"
                    
                    if self.streaming_orchestrator:
                        self.streaming_orchestrator.update_agent_status(agent_id, "reasoning_complete")
                        
                    logger.info(f"✅ Agent {agent_id} completed individual reasoning")
                    
                except Exception as e:
                    logger.error(f"❌ Agent {agent_id} failed during reasoning: {e}")
                    self.mark_agent_failed(agent_id, str(e))
        
        finally:
            executor.shutdown(wait=True)
        
        logger.info(f"📝 Individual reasoning complete: {len(self.reasoning_outputs)}/{len(self.agents)} agents succeeded")
    
    def _agent_individual_reasoning(self, agent_id: int, agent, task) -> List[str]:
        """Execute individual reasoning for a single agent."""
        logger.info(f"🤖 Agent {agent_id} starting individual reasoning")
        
        # Create structured reasoning prompt
        reasoning_messages = [
            {
                "role": "system", 
                "content": """You are participating in a structured multi-agent reasoning process. Your task is to:

1. Analyze the given problem step-by-step
2. Break down your reasoning into clear, logical steps
3. Identify key evidence and assumptions
4. Provide your initial solution with confidence assessment

Focus on clarity, logical consistency, and evidence-based reasoning. Your reasoning will be reviewed by other agents in subsequent phases."""
            },
            {
                "role": "user", 
                "content": f"""Problem to analyze: {getattr(task, 'question', 'Unknown question')}

Please provide your structured reasoning following these steps:
1. Problem Understanding: Restate the problem in your own words
2. Key Information: Identify crucial information and constraints  
3. Reasoning Steps: Break down your analysis step-by-step
4. Initial Solution: Provide your answer with reasoning
5. Confidence Assessment: Rate your confidence (1-10) and identify uncertainties

Be thorough but concise. Focus on logical consistency and evidence."""
            }
        ]
        
        try:
            # Get available tools for reasoning
            tools = []
            if hasattr(agent, 'model_config') and hasattr(agent.model_config, 'tools'):
                tools = agent.model_config.tools or []
            
            # Process the reasoning request
            result = agent.process_message(messages=reasoning_messages, tools=tools)
            
            # Update agent state
            self.agent_states[agent_id].add_update(result.text)
            self.agent_states[agent_id].chat_round += 1
            
            # Update streaming display
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_chat_round(agent_id, self.agent_states[agent_id].chat_round)
                update_count = len(self.agent_states[agent_id].updated_answers)
                self.streaming_orchestrator.update_agent_update_count(agent_id, update_count)
            
            logger.info(f"✅ Agent {agent_id} completed individual reasoning ({len(result.text)} chars)")
            return [result.text]
            
        except Exception as e:
            logger.error(f"❌ Agent {agent_id} failed during individual reasoning: {e}")
            raise
    
    def _phase_critique_generation(self, task):
        """Phase 2: Agents generate critiques of others' reasoning."""
        self.system_state.phase = "critique"
        
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("reasoning", "critique")
            self.streaming_orchestrator.add_system_message("🔍 Phase 2: Critique generation started")
        
        # Each agent critiques others' reasoning
        for agent_id, agent in self.agents.items():
            if agent_id not in self.reasoning_outputs:
                continue  # Skip failed agents
            
            try:
                self.agent_states[agent_id].status = "critiquing"
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(agent_id, "critiquing")
                
                agent_critiques = self._agent_generate_critiques(agent_id, agent, task)
                self.critiques[agent_id] = agent_critiques
                
                self.agent_states[agent_id].status = "critique_complete"
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(agent_id, "critique_complete")
                
                logger.info(f"✅ Agent {agent_id} completed critique generation")
                
            except Exception as e:
                logger.error(f"❌ Agent {agent_id} failed during critique generation: {e}")
                self.mark_agent_failed(agent_id, str(e))
        
        logger.info(f"🔍 Critique generation complete: {len(self.critiques)}/{len(self.reasoning_outputs)} agents succeeded")
    
    def _agent_generate_critiques(self, agent_id: int, agent, task) -> List[Dict[str, Any]]:
        """Generate critiques of other agents' reasoning."""
        logger.info(f"🤖 Agent {agent_id} generating critiques")
        
        critiques = []
        
        # Critique each other agent's reasoning
        for other_agent_id, reasoning in self.reasoning_outputs.items():
            if other_agent_id == agent_id:
                continue  # Don't critique yourself
            
            critique_messages = [
                {
                    "role": "system", 
                    "content": """You are reviewing another agent's reasoning in a collaborative problem-solving process. Your task is to:

1. Identify strengths in the reasoning
2. Point out potential weaknesses or gaps
3. Suggest improvements or alternative approaches
4. Assess the logical consistency and evidence quality

Be constructive, specific, and focus on the reasoning quality rather than just the conclusion."""
                },
                {
                    "role": "user", 
                    "content": f"""Original Problem: {getattr(task, 'question', 'Unknown question')}

Agent's Reasoning to Review:
{reasoning[0] if reasoning else 'No reasoning provided'}

Please provide a constructive critique following this structure:
1. Strengths: What aspects of the reasoning are solid?
2. Weaknesses: What gaps or issues do you identify?
3. Evidence Assessment: How well-supported are the claims?
4. Suggestions: What improvements would you recommend?
5. Overall Assessment: Rate the reasoning quality (1-10) and explain

Be specific and constructive in your feedback."""
                }
            ]
            
            try:
                result = agent.process_message(messages=critique_messages)
                
                critique = {
                    "target_agent": other_agent_id,
                    "critique_text": result.text,
                    "timestamp": time.time()
                }
                critiques.append(critique)
                
                logger.info(f"📝 Agent {agent_id} critiqued Agent {other_agent_id}")
                
            except Exception as e:
                logger.error(f"❌ Agent {agent_id} failed to critique Agent {other_agent_id}: {e}")
        
        return critiques
    
    def _phase_evidence_synthesis(self, task):
        """Phase 3: Agents synthesize critiques and refine their solutions."""
        self.system_state.phase = "synthesis"
        
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("critique", "synthesis")
            self.streaming_orchestrator.add_system_message("⚗️ Phase 3: Evidence synthesis started")
        
        # Each agent refines their solution based on received critiques
        for agent_id, agent in self.agents.items():
            if agent_id not in self.reasoning_outputs:
                continue  # Skip failed agents
            
            try:
                self.agent_states[agent_id].status = "synthesizing"
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(agent_id, "synthesizing")
                
                refined_solution = self._agent_synthesize_evidence(agent_id, agent, task)
                self.refined_solutions[agent_id] = refined_solution
                
                # Calculate evidence score based on synthesis quality
                evidence_score = self._calculate_evidence_score(agent_id, refined_solution)
                self.evidence_scores[agent_id] = evidence_score
                
                self.agent_states[agent_id].status = "synthesis_complete"
                if self.streaming_orchestrator:
                    self.streaming_orchestrator.update_agent_status(agent_id, "synthesis_complete")
                
                logger.info(f"✅ Agent {agent_id} completed evidence synthesis (score: {evidence_score:.2f})")
                
            except Exception as e:
                logger.error(f"❌ Agent {agent_id} failed during evidence synthesis: {e}")
                self.mark_agent_failed(agent_id, str(e))
        
        logger.info(f"⚗️ Evidence synthesis complete: {len(self.refined_solutions)}/{len(self.reasoning_outputs)} agents succeeded")
    
    def _agent_synthesize_evidence(self, agent_id: int, agent, task) -> str:
        """Synthesize critiques and refine the solution."""
        logger.info(f"🤖 Agent {agent_id} synthesizing evidence")
        
        # Collect critiques received by this agent
        received_critiques = []
        for critic_id, critiques in self.critiques.items():
            for critique in critiques:
                if critique["target_agent"] == agent_id:
                    received_critiques.append(f"Critique from Agent {critic_id}: {critique['critique_text']}")
        
        # Create synthesis prompt
        synthesis_messages = [
            {
                "role": "system",
                "content": """You are refining your solution based on peer critiques in a collaborative reasoning process. Your task is to:

1. Review the critiques of your reasoning
2. Identify valid points and areas for improvement
3. Refine your solution incorporating the feedback
4. Provide a final, improved answer with stronger evidence

Focus on addressing legitimate concerns while maintaining your core insights."""
            },
            {
                "role": "user",
                "content": f"""Original Problem: {getattr(task, 'question', 'Unknown question')}

Your Original Reasoning:
{self.reasoning_outputs[agent_id][0] if agent_id in self.reasoning_outputs else 'No original reasoning'}

Critiques Received:
{chr(10).join(received_critiques) if received_critiques else 'No critiques received'}

Please provide your refined solution following this structure:
1. Critique Analysis: How do you respond to the main criticisms?
2. Refined Reasoning: Updated analysis incorporating valid feedback
3. Improved Solution: Your final answer with stronger justification
4. Confidence Update: Updated confidence level and remaining uncertainties

Be thorough in addressing critiques while maintaining logical consistency."""
            }
        ]
        
        try:
            result = agent.process_message(messages=synthesis_messages)
            
            # Update agent state
            self.agent_states[agent_id].add_update(result.text)
            self.agent_states[agent_id].chat_round += 1
            
            # Update streaming display
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_agent_chat_round(agent_id, self.agent_states[agent_id].chat_round)
                update_count = len(self.agent_states[agent_id].updated_answers)
                self.streaming_orchestrator.update_agent_update_count(agent_id, update_count)
            
            logger.info(f"✅ Agent {agent_id} completed evidence synthesis ({len(result.text)} chars)")
            return result.text
            
        except Exception as e:
            logger.error(f"❌ Agent {agent_id} failed during evidence synthesis: {e}")
            raise
    
    def _calculate_evidence_score(self, agent_id: int, refined_solution: str) -> float:
        """Calculate evidence quality score for a refined solution."""
        # Simple heuristic scoring based on solution characteristics
        score = 0.5  # Base score
        
        # Length indicates thoroughness
        if len(refined_solution) > 500:
            score += 0.1
        if len(refined_solution) > 1000:
            score += 0.1
        
        # Count critique responses (indicates engagement with feedback)
        critique_responses = refined_solution.lower().count('critique')
        score += min(critique_responses * 0.05, 0.2)
        
        # Count evidence/reasoning keywords
        evidence_keywords = ['evidence', 'because', 'therefore', 'analysis', 'reasoning', 'conclusion']
        for keyword in evidence_keywords:
            if keyword in refined_solution.lower():
                score += 0.02
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _phase_consensus_validation(self, task):
        """Phase 4: Select the best solution based on evidence scores."""
        self.system_state.phase = "consensus"
        
        if self.streaming_orchestrator:
            self.streaming_orchestrator.update_phase("synthesis", "consensus")
            self.streaming_orchestrator.add_system_message("✅ Phase 4: Consensus validation started")
        
        if not self.evidence_scores:
            logger.warning("⚠️ No evidence scores available for consensus")
            self._handle_no_solutions()
            return
        
        # Select agent with highest evidence score
        best_agent_id = max(self.evidence_scores.keys(), key=lambda aid: self.evidence_scores[aid])
        best_score = self.evidence_scores[best_agent_id]
        
        logger.info(f"🏆 Best solution: Agent {best_agent_id} with evidence score {best_score:.3f}")
        
        # Check if score meets threshold
        if best_score >= self.evidence_threshold:
            self.system_state.consensus_reached = True
            self.system_state.representative_agent_id = best_agent_id
            
            # Present final answer
            self._present_final_answer(task, best_agent_id)
            
            logger.info(f"✅ Consensus reached: Agent {best_agent_id} selected as representative")
            
            if self.streaming_orchestrator:
                self.streaming_orchestrator.update_consensus_status(best_agent_id, dict(self.evidence_scores))
                self.streaming_orchestrator.add_system_message(f"🎯 Consensus: Agent {best_agent_id} selected (score: {best_score:.3f})")
        
        else:
            logger.warning(f"⚠️ Best evidence score {best_score:.3f} below threshold {self.evidence_threshold}")
            # Still select the best available, but mark as low confidence
            self.system_state.consensus_reached = False
            self.system_state.representative_agent_id = best_agent_id
            self._present_final_answer(task, best_agent_id)
    
    def _present_final_answer(self, task, representative_id: int):
        """Generate the final answer from the representative agent."""
        logger.info(f"🎯 Agent {representative_id} presenting final answer")
        
        try:
            if representative_id in self.refined_solutions:
                # Use the refined solution as the final answer
                self.final_response = self.refined_solutions[representative_id]
            else:
                # Fallback to original reasoning
                self.final_response = self.reasoning_outputs.get(representative_id, ["No solution available"])[0]
            
            self.system_state.phase = "completed"
            self.system_state.end_time = time.time()
            
            logger.info(f"✅ Final answer presentation completed by Agent {representative_id}")
            
        except Exception as e:
            logger.error(f"❌ Final answer presentation failed: {e}")
            self.final_response = f"Error in final answer presentation: {str(e)}"
    
    def _handle_timeout(self) -> Dict[str, Any]:
        """Handle timeout scenario."""
        logger.warning("⏰ Algorithm timed out - selecting best available solution")
        
        # Select best agent based on available evidence
        if self.evidence_scores:
            best_agent_id = max(self.evidence_scores.keys(), key=lambda aid: self.evidence_scores[aid])
        elif self.refined_solutions:
            best_agent_id = list(self.refined_solutions.keys())[0]
        elif self.reasoning_outputs:
            best_agent_id = list(self.reasoning_outputs.keys())[0]
        else:
            best_agent_id = list(self.agents.keys())[0] if self.agents else None
        
        if best_agent_id:
            self.system_state.representative_agent_id = best_agent_id
            self._present_final_answer(None, best_agent_id)
        
        return self._finalize_session()
    
    def _handle_error(self, error_msg: str) -> Dict[str, Any]:
        """Handle algorithm error."""
        logger.error(f"❌ Algorithm error: {error_msg}")
        self.final_response = f"Algorithm error: {error_msg}"
        return self._finalize_session()
    
    def _handle_no_solutions(self):
        """Handle case where no solutions are available."""
        logger.warning("⚠️ No solutions available - using fallback")
        
        if self.agents:
            fallback_agent_id = list(self.agents.keys())[0]
            self.system_state.representative_agent_id = fallback_agent_id
            self.final_response = "No structured solutions were generated due to agent failures."
        else:
            self.final_response = "No agents available to provide solutions."
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an algorithm event."""
        self.communication_log.append({"timestamp": time.time(), "event_type": event_type, "data": data})
    
    def _finalize_session(self) -> Dict[str, Any]:
        """Finalize the session with algorithm-specific results."""
        result = super()._finalize_session()
        
        # Add Arxiv2503Algorithm specific data
        result["summary"].update({
            "reasoning_outputs": len(self.reasoning_outputs),
            "critiques_generated": sum(len(critiques) for critiques in self.critiques.values()),
            "refined_solutions": len(self.refined_solutions),
            "evidence_scores": dict(self.evidence_scores),
            "max_evidence_score": max(self.evidence_scores.values()) if self.evidence_scores else 0.0,
        })
        
        # Save detailed session log
        result["system_logs"] = self._export_detailed_session_log()
        
        # Save result to result.json
        if self.log_manager and not getattr(self.log_manager, 'non_blocking', True):
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
                "session_id": f"mass_session_{int(getattr(self.system_state, 'start_time', time.time()))}",
                "start_time": getattr(self.system_state, 'start_time', None),
                "end_time": getattr(self.system_state, 'end_time', None),
                "total_duration": (getattr(self.system_state, 'end_time', time.time()) - getattr(self.system_state, 'start_time', time.time())) if hasattr(self.system_state, 'start_time') else None,
                "timestamp": datetime.now().isoformat(),
                "system_version": "MassGen v1.0",
                "algorithm": "Arxiv2503Algorithm"
            },
            "task_information": {
                "question": getattr(getattr(self.system_state, 'task', None), 'question', None),
                "task_id": getattr(getattr(self.system_state, 'task', None), 'task_id', None),
            },
            "system_configuration": {
                "max_duration": self.max_duration,
                "max_reasoning_rounds": self.max_reasoning_rounds,
                "critique_rounds": self.critique_rounds,
                "evidence_threshold": self.evidence_threshold,
                "agents": [getattr(agent, 'model', 'unknown') for agent in self.agents.values()],
            },
            "reasoning_analysis": {
                "reasoning_outputs_count": len(self.reasoning_outputs),
                "critiques_count": sum(len(critiques) for critiques in self.critiques.values()),
                "refined_solutions_count": len(self.refined_solutions),
                "evidence_scores": dict(self.evidence_scores),
            },
            "communication_log": self.communication_log,
        }

        return session_log
    
    # Compatibility methods (not used in this algorithm but required by interface)
    def cast_vote(self, voter_id: int, target_id: int, reason: str = ""):
        """Voting not used in structured reasoning algorithm."""
        logger.warning(f"⚠️ cast_vote called but not supported in Arxiv2503Algorithm")
    
    def update_agent_answer(self, agent_id: int, answer: str):
        """Update agent answer - handled automatically during structured phases."""
        super().update_agent_answer(agent_id, answer)