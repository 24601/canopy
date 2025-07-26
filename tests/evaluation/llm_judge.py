"""LLM-as-judge evaluation framework for multi-agent consensus quality."""

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from canopy_core.algorithms.base import AlgorithmResult
    from canopy_core.types import TaskInput


@dataclass
class EvaluationCriteria:
    """Criteria for evaluating multi-agent responses."""

    name: str
    description: str
    weight: float = 1.0
    rubric: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of LLM-as-judge evaluation."""

    task_id: str
    overall_score: float
    criteria_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    consensus_quality: str
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMJudge:
    """LLM-based evaluation system for multi-agent outputs."""

    DEFAULT_CRITERIA = [
        EvaluationCriteria(
            name="correctness",
            description="Is the answer factually correct and accurate?",
            weight=2.0,
            rubric={
                "5": "Completely correct with no errors",
                "4": "Mostly correct with minor inaccuracies",
                "3": "Partially correct with some errors",
                "2": "Mostly incorrect with major errors",
                "1": "Completely incorrect or nonsensical",
            },
        ),
        EvaluationCriteria(
            name="completeness",
            description="Does the answer fully address all aspects of the question?",
            weight=1.5,
            rubric={
                "5": "Comprehensively addresses all aspects",
                "4": "Addresses most important aspects",
                "3": "Addresses main points but misses some details",
                "2": "Addresses only basic aspects",
                "1": "Fails to address key aspects",
            },
        ),
        EvaluationCriteria(
            name="coherence",
            description="Is the answer well-structured and logically organized?",
            weight=1.0,
            rubric={
                "5": "Exceptionally clear and well-organized",
                "4": "Clear with good logical flow",
                "3": "Generally coherent with minor issues",
                "2": "Some coherence but disorganized",
                "1": "Incoherent or severely disorganized",
            },
        ),
        EvaluationCriteria(
            name="consensus_quality",
            description="How well did the agents reach meaningful consensus?",
            weight=1.5,
            rubric={
                "5": "Strong consensus with complementary insights",
                "4": "Good consensus with aligned reasoning",
                "3": "Basic consensus with some alignment",
                "2": "Weak consensus or forced agreement",
                "1": "No real consensus or contradictory views",
            },
        ),
    ]

    def __init__(
        self,
        judge_model: Optional[Any] = None,
        criteria: Optional[List[EvaluationCriteria]] = None,
    ):
        """Initialize the LLM judge.

        Args:
            judge_model: The LLM model to use for judging (e.g., GPT-4, Claude)
            criteria: Custom evaluation criteria (uses defaults if not provided)
        """
        self.judge_model = judge_model
        self.criteria = criteria or self.DEFAULT_CRITERIA

    def evaluate(
        self,
        task: TaskInput,
        result: AlgorithmResult,
        ground_truth: Optional[str] = None,
    ) -> EvaluationResult:
        """Evaluate a multi-agent result using LLM-as-judge.

        Args:
            task: The original task input
            result: The algorithm result to evaluate
            ground_truth: Optional ground truth answer for comparison

        Returns:
            Comprehensive evaluation result
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(task, result, ground_truth)

        # Get LLM judgment
        judgment = self._get_llm_judgment(prompt)

        # Parse and structure the evaluation
        task_id = task.task_id or "unknown"
        return self._parse_judgment(judgment, task_id)

    def _build_evaluation_prompt(self, task: TaskInput, result: AlgorithmResult, ground_truth: Optional[str]) -> str:
        """Build the evaluation prompt for the judge LLM."""
        prompt = f"""You are an expert evaluator assessing the quality of a multi-agent system's response.

**Original Question:**
{task.question}

**Multi-Agent System Response:**
{result.answer}

**Consensus Information:**
- Consensus reached: {result.consensus_reached}
- Number of agents: {len(result.metadata.get('agent_responses', []))}
- Debate rounds: {result.algorithm_specific_data.get('debate_rounds', 0)}

"""

        if ground_truth:
            prompt += f"""**Reference Answer (Ground Truth):**
{ground_truth}

"""

        prompt += """**Evaluation Criteria:**
Please evaluate the response on the following criteria, providing a score from 1-5 for each:

"""

        for criterion in self.criteria:
            prompt += f"\n{criterion.name.upper()} ({criterion.description}):\n"
            for score, description in sorted(criterion.rubric.items(), reverse=True):
                prompt += f"  {score}: {description}\n"

        prompt += """
**Required Output Format:**
Provide your evaluation in the following JSON format:
{
    "criteria_scores": {
        "correctness": <1-5>,
        "completeness": <1-5>,
        "coherence": <1-5>,
        "consensus_quality": <1-5>
    },
    "strengths": ["strength1", "strength2", ...],
    "weaknesses": ["weakness1", "weakness2", ...],
    "consensus_quality_assessment": "<detailed assessment of how well agents reached consensus>",
    "overall_reasoning": "<comprehensive reasoning for the evaluation>"
}
"""

        return prompt

    def _get_llm_judgment(self, prompt: str) -> Dict[str, Any]:
        """Get judgment from the LLM judge."""
        if self.judge_model is None:
            # Return mock judgment for testing
            return {
                "criteria_scores": {
                    "correctness": 4,
                    "completeness": 4,
                    "coherence": 5,
                    "consensus_quality": 4,
                },
                "strengths": ["Clear reasoning", "Well-structured response"],
                "weaknesses": ["Could be more comprehensive"],
                "consensus_quality_assessment": "Agents reached good consensus",
                "overall_reasoning": "The response demonstrates good quality overall",
            }

        # In real implementation, call the judge model
        # response = self.judge_model.generate(prompt)
        # return json.loads(response)

        # For now, return mock judgment until real implementation
        return {
            "criteria_scores": {
                "correctness": 4,
                "completeness": 4,
                "coherence": 5,
                "consensus_quality": 4,
            },
            "strengths": ["Clear reasoning", "Well-structured response"],
            "weaknesses": ["Could be more comprehensive"],
            "consensus_quality_assessment": "Agents reached good consensus",
            "overall_reasoning": "The response demonstrates good quality overall",
        }

    def _parse_judgment(self, judgment: Dict[str, Any], task_id: str) -> EvaluationResult:
        """Parse LLM judgment into structured evaluation result."""
        criteria_scores = judgment.get("criteria_scores", {})

        # Calculate weighted overall score
        total_weight = sum(c.weight for c in self.criteria)
        weighted_sum = sum(criteria_scores.get(c.name, 3) * c.weight for c in self.criteria)
        overall_score = weighted_sum / total_weight

        return EvaluationResult(
            task_id=task_id,
            overall_score=overall_score,
            criteria_scores=criteria_scores,
            strengths=judgment.get("strengths", []),
            weaknesses=judgment.get("weaknesses", []),
            consensus_quality=judgment.get("consensus_quality_assessment", ""),
            reasoning=judgment.get("overall_reasoning", ""),
            metadata={"judgment_timestamp": time.time()},
        )

    def evaluate_batch(
        self,
        tasks_results: List[Tuple[TaskInput, AlgorithmResult]],
        ground_truths: Optional[Dict[str, str]] = None,
    ) -> List[EvaluationResult]:
        """Evaluate a batch of task results.

        Args:
            tasks_results: List of (task, result) tuples
            ground_truths: Optional dict mapping task_id to ground truth answers

        Returns:
            List of evaluation results
        """
        ground_truths = ground_truths or {}
        evaluations = []

        for task, result in tasks_results:
            task_id = task.task_id or "unknown"
            ground_truth = ground_truths.get(task_id)
            evaluation = self.evaluate(task, result, ground_truth)
            evaluations.append(evaluation)

        return evaluations

    def generate_report(self, evaluations: List[EvaluationResult]) -> Dict[str, Any]:
        """Generate a summary report from multiple evaluations."""
        if not evaluations:
            return {"error": "No evaluations to report"}

        # Calculate aggregate statistics
        avg_overall = sum(e.overall_score for e in evaluations) / len(evaluations)

        criteria_avgs = {}
        for criterion in self.criteria:
            scores = [e.criteria_scores.get(criterion.name, 0) for e in evaluations]
            criteria_avgs[criterion.name] = sum(scores) / len(scores) if scores else 0

        # Identify common strengths and weaknesses
        all_strengths = [s for e in evaluations for s in e.strengths]
        all_weaknesses = [w for e in evaluations for w in e.weaknesses]

        return {
            "summary": {
                "total_evaluations": len(evaluations),
                "average_overall_score": round(avg_overall, 2),
                "criteria_averages": {k: round(v, 2) for k, v in criteria_avgs.items()},
            },
            "insights": {
                "common_strengths": self._get_top_items(all_strengths, 5),
                "common_weaknesses": self._get_top_items(all_weaknesses, 5),
                "best_performing": max(evaluations, key=lambda e: e.overall_score).task_id,
                "worst_performing": min(evaluations, key=lambda e: e.overall_score).task_id,
            },
            "distribution": {
                "excellent": sum(1 for e in evaluations if e.overall_score >= 4.5),
                "good": sum(1 for e in evaluations if 3.5 <= e.overall_score < 4.5),
                "fair": sum(1 for e in evaluations if 2.5 <= e.overall_score < 3.5),
                "poor": sum(1 for e in evaluations if e.overall_score < 2.5),
            },
        }

    def _get_top_items(self, items: List[str], n: int = 5) -> List[Tuple[str, int]]:
        """Get top N most common items with counts."""
        from collections import Counter

        counter = Counter(items)
        return counter.most_common(n)
