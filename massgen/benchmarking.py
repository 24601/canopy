"""
Benchmarking Framework for MassGen Algorithms

This module provides comprehensive benchmarking capabilities for comparing
different multi-agent orchestration algorithms on various tasks and metrics.

Features:
- Task-based performance comparison
- Metric collection (time, accuracy, consensus quality)
- Statistical analysis and reporting
- Extensible benchmark suite
- Export results in multiple formats
"""

import time
import json
import logging
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTask:
    """Represents a single benchmark task."""
    
    task_id: str
    question: str
    category: str
    difficulty: str  # "easy", "medium", "hard"
    expected_answer: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BenchmarkResult:
    """Results for a single algorithm on a single task."""
    
    algorithm_name: str
    task_id: str
    answer: str
    consensus_reached: bool
    session_duration: float
    representative_agent_id: Optional[int]
    
    # Algorithm-specific metrics
    total_agents: int = 0
    failed_agents: int = 0
    success_rate: float = 0.0
    
    # Extended metrics (algorithm-dependent)
    extended_metrics: Optional[Dict[str, Any]] = None
    
    # Evaluation results
    correctness_score: Optional[float] = None  # 0.0 - 1.0
    quality_score: Optional[float] = None      # 0.0 - 1.0
    efficiency_score: Optional[float] = None   # 0.0 - 1.0
    
    timestamp: float = 0.0
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass 
class BenchmarkSummary:
    """Summary statistics for algorithm performance across tasks."""
    
    algorithm_name: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    success_rate: float
    
    # Time metrics
    avg_duration: float
    min_duration: float
    max_duration: float
    
    # Quality metrics (when available)
    avg_correctness: Optional[float] = None
    avg_quality: Optional[float] = None
    avg_efficiency: Optional[float] = None
    
    # Consensus metrics
    consensus_rate: float = 0.0
    avg_agents_used: float = 0.0
    avg_failure_rate: float = 0.0
    
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class BenchmarkSuite:
    """
    Comprehensive benchmarking suite for MassGen algorithms.
    
    This class manages benchmark tasks, executes algorithms, collects metrics,
    and generates comparative reports.
    """
    
    def __init__(self, output_dir: str = "benchmark_results"):
        """
        Initialize the benchmark suite.
        
        Args:
            output_dir: Directory to save benchmark results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.tasks: List[BenchmarkTask] = []
        self.results: List[BenchmarkResult] = []
        self.evaluators: Dict[str, Callable] = {}
        
        logger.info(f"🧪 BenchmarkSuite initialized with output_dir: {self.output_dir}")
    
    def add_task(self, task: BenchmarkTask):
        """Add a benchmark task to the suite."""
        self.tasks.append(task)
        logger.info(f"📝 Added benchmark task: {task.task_id} ({task.category}/{task.difficulty})")
    
    def add_tasks_from_file(self, file_path: str):
        """Load benchmark tasks from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        for task_data in tasks_data:
            task = BenchmarkTask(**task_data)
            self.add_task(task)
        
        logger.info(f"📂 Loaded {len(tasks_data)} tasks from {file_path}")
    
    def add_evaluator(self, name: str, evaluator_func: Callable):
        """
        Add a custom evaluator function.
        
        Args:
            name: Name of the evaluator
            evaluator_func: Function that takes (task, result) and returns score (0.0-1.0)
        """
        self.evaluators[name] = evaluator_func
        logger.info(f"⚖️ Added evaluator: {name}")
    
    def create_default_tasks(self):
        """Create a default set of benchmark tasks."""
        default_tasks = [
            BenchmarkTask(
                task_id="math_basic_001",
                question="What is 15 * 23 + 7?",
                category="mathematics",
                difficulty="easy",
                expected_answer="352"
            ),
            BenchmarkTask(
                task_id="logic_basic_001", 
                question="If all cats are animals, and some animals are pets, can we conclude that some cats are pets?",
                category="logic",
                difficulty="medium",
                expected_answer="No, we cannot conclude that. The premises don't provide enough information."
            ),
            BenchmarkTask(
                task_id="reasoning_complex_001",
                question="A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?",
                category="reasoning", 
                difficulty="medium",
                expected_answer="$0.05"
            ),
            BenchmarkTask(
                task_id="analysis_hard_001",
                question="Analyze the potential economic impacts of implementing a universal basic income policy in a developed country with 50 million citizens.",
                category="analysis",
                difficulty="hard"
            ),
            BenchmarkTask(
                task_id="creativity_001",
                question="Design a sustainable transportation system for a city of 2 million people that reduces carbon emissions by 70% within 10 years.",
                category="creativity",
                difficulty="hard"
            )
        ]
        
        for task in default_tasks:
            self.add_task(task)
        
        logger.info(f"✨ Created {len(default_tasks)} default benchmark tasks")
    
    def run_benchmark(
        self, 
        algorithms: List[str],
        config_template: Optional[Dict[str, Any]] = None,
        max_workers: int = 2,
        timeout_per_task: int = 300
    ) -> Dict[str, List[BenchmarkResult]]:
        """
        Run benchmarks for multiple algorithms on all tasks.
        
        Args:
            algorithms: List of algorithm names to benchmark
            config_template: Base configuration template for algorithms
            max_workers: Maximum concurrent benchmark workers
            timeout_per_task: Timeout per task in seconds
            
        Returns:
            Dict mapping algorithm names to their results
        """
        if not self.tasks:
            raise ValueError("No benchmark tasks defined. Add tasks first.")
        
        logger.info(f"🚀 Starting benchmark run")
        logger.info(f"   Algorithms: {algorithms}")
        logger.info(f"   Tasks: {len(self.tasks)}")
        logger.info(f"   Max workers: {max_workers}")
        
        all_results = {}
        
        # Run benchmarks for each algorithm
        for algorithm_name in algorithms:
            logger.info(f"🔬 Benchmarking algorithm: {algorithm_name}")
            
            algorithm_results = []
            start_time = time.time()
            
            # Use ThreadPoolExecutor for parallel task execution
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks for this algorithm
                future_to_task = {
                    executor.submit(
                        self._run_single_benchmark, 
                        algorithm_name, 
                        task, 
                        config_template,
                        timeout_per_task
                    ): task 
                    for task in self.tasks
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        algorithm_results.append(result)
                        
                        status = "✅" if not result.error else "❌"
                        logger.info(f"   {status} {task.task_id} - {result.session_duration:.1f}s")
                        
                    except Exception as e:
                        error_result = BenchmarkResult(
                            algorithm_name=algorithm_name,
                            task_id=task.task_id,
                            answer="",
                            consensus_reached=False,
                            session_duration=0.0,
                            representative_agent_id=None,
                            error=str(e)
                        )
                        algorithm_results.append(error_result)
                        logger.error(f"   ❌ {task.task_id} failed: {e}")
            
            total_time = time.time() - start_time
            logger.info(f"✅ {algorithm_name} completed in {total_time:.1f}s")
            
            all_results[algorithm_name] = algorithm_results
            self.results.extend(algorithm_results)
        
        # Evaluate results if evaluators are available
        self._evaluate_results()
        
        return all_results
    
    def _run_single_benchmark(
        self, 
        algorithm_name: str, 
        task: BenchmarkTask,
        config_template: Optional[Dict[str, Any]],
        timeout: int
    ) -> BenchmarkResult:
        """Run a single benchmark task for one algorithm."""
        try:
            # Import here to avoid circular imports
            from ..algorithms import create_algorithm
            from ..config import create_config_from_models
            from ..main import run_mass_with_config
            
            # Create algorithm configuration
            config = create_config_from_models(
                models=["gpt-4o", "gemini-2.5-flash"],  # Default models for benchmarking
                orchestrator_config={
                    "algorithm": algorithm_name,
                    "max_duration": timeout,
                    **(config_template or {})
                },
                streaming_config={"display_enabled": False},  # Disable UI for benchmarking
                logging_config={"non_blocking": True}         # Non-blocking logging
            )
            
            # Run the task
            start_time = time.time()
            result = run_mass_with_config(task.question, config)
            duration = time.time() - start_time
            
            # Extract metrics
            summary = result.get("summary", {})
            extended_metrics = {}
            
            # Algorithm-specific metrics
            if algorithm_name == "arxiv_2503_04412":
                extended_metrics = {
                    "evidence_scores": summary.get("evidence_scores", {}),
                    "reasoning_outputs": summary.get("reasoning_outputs", 0),
                    "critiques_generated": summary.get("critiques_generated", 0),
                    "refined_solutions": summary.get("refined_solutions", 0),
                }
            elif algorithm_name == "default":
                extended_metrics = {
                    "total_votes": summary.get("total_votes", 0),
                    "final_vote_distribution": summary.get("final_vote_distribution", {}),
                }
            
            # Create benchmark result
            benchmark_result = BenchmarkResult(
                algorithm_name=algorithm_name,
                task_id=task.task_id,
                answer=result["answer"],
                consensus_reached=result.get("consensus_reached", False),
                session_duration=duration,
                representative_agent_id=result.get("representative_agent_id"),
                total_agents=summary.get("total_agents", 0),
                failed_agents=summary.get("failed_agents", 0),
                success_rate=1.0 - (summary.get("failed_agents", 0) / max(summary.get("total_agents", 1), 1)),
                extended_metrics=extended_metrics
            )
            
            return benchmark_result
            
        except Exception as e:
            logger.error(f"❌ Benchmark failed for {algorithm_name} on {task.task_id}: {e}")
            return BenchmarkResult(
                algorithm_name=algorithm_name,
                task_id=task.task_id,
                answer="",
                consensus_reached=False,
                session_duration=0.0,
                representative_agent_id=None,
                error=str(e)
            )
    
    def _evaluate_results(self):
        """Evaluate benchmark results using registered evaluators."""
        if not self.evaluators:
            logger.info("⚖️ No evaluators registered - skipping evaluation")
            return
        
        logger.info(f"⚖️ Evaluating results with {len(self.evaluators)} evaluators")
        
        for result in self.results:
            if result.error:
                continue  # Skip failed results
            
            # Find corresponding task
            task = next((t for t in self.tasks if t.task_id == result.task_id), None)
            if not task:
                continue
            
            # Apply evaluators
            for evaluator_name, evaluator_func in self.evaluators.items():
                try:
                    score = evaluator_func(task, result)
                    
                    # Map evaluator names to result fields
                    if evaluator_name == "correctness":
                        result.correctness_score = score
                    elif evaluator_name == "quality":
                        result.quality_score = score
                    elif evaluator_name == "efficiency":
                        result.efficiency_score = score
                        
                except Exception as e:
                    logger.error(f"❌ Evaluator {evaluator_name} failed for {result.task_id}: {e}")
    
    def generate_summary(self) -> Dict[str, BenchmarkSummary]:
        """Generate summary statistics for each algorithm."""
        if not self.results:
            logger.warning("⚠️ No results available for summary generation")
            return {}
        
        logger.info("📊 Generating benchmark summary statistics")
        
        # Group results by algorithm
        algorithm_results = {}
        for result in self.results:
            if result.algorithm_name not in algorithm_results:
                algorithm_results[result.algorithm_name] = []
            algorithm_results[result.algorithm_name].append(result)
        
        # Generate summaries
        summaries = {}
        for algorithm_name, results in algorithm_results.items():
            successful_results = [r for r in results if not r.error]
            failed_results = [r for r in results if r.error]
            
            if successful_results:
                durations = [r.session_duration for r in successful_results]
                consensus_reached = [r for r in successful_results if r.consensus_reached]
                
                # Calculate quality metrics if available
                correctness_scores = [r.correctness_score for r in successful_results if r.correctness_score is not None]
                quality_scores = [r.quality_score for r in successful_results if r.quality_score is not None]
                efficiency_scores = [r.efficiency_score for r in successful_results if r.efficiency_score is not None]
                
                summary = BenchmarkSummary(
                    algorithm_name=algorithm_name,
                    total_tasks=len(results),
                    successful_tasks=len(successful_results),
                    failed_tasks=len(failed_results),
                    success_rate=len(successful_results) / len(results),
                    avg_duration=statistics.mean(durations),
                    min_duration=min(durations),
                    max_duration=max(durations),
                    avg_correctness=statistics.mean(correctness_scores) if correctness_scores else None,
                    avg_quality=statistics.mean(quality_scores) if quality_scores else None,
                    avg_efficiency=statistics.mean(efficiency_scores) if efficiency_scores else None,
                    consensus_rate=len(consensus_reached) / len(successful_results),
                    avg_agents_used=statistics.mean([r.total_agents for r in successful_results]),
                    avg_failure_rate=statistics.mean([r.failed_agents / max(r.total_agents, 1) for r in successful_results])
                )
            else:
                # All results failed
                summary = BenchmarkSummary(
                    algorithm_name=algorithm_name,
                    total_tasks=len(results),
                    successful_tasks=0,
                    failed_tasks=len(failed_results),
                    success_rate=0.0,
                    avg_duration=0.0,
                    min_duration=0.0,
                    max_duration=0.0,
                    consensus_rate=0.0,
                    avg_agents_used=0.0,
                    avg_failure_rate=1.0
                )
            
            summaries[algorithm_name] = summary
        
        return summaries
    
    def export_results(self, format: str = "json", filename: Optional[str] = None) -> str:
        """
        Export benchmark results to file.
        
        Args:
            format: Export format ("json", "csv", "html")
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.{format}"
        
        output_path = self.output_dir / filename
        
        if format == "json":
            self._export_json(output_path)
        elif format == "csv":
            self._export_csv(output_path)
        elif format == "html":
            self._export_html(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"📁 Exported benchmark results to: {output_path}")
        return str(output_path)
    
    def _export_json(self, output_path: Path):
        """Export results as JSON."""
        summaries = self.generate_summary()
        
        export_data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_tasks": len(self.tasks),
                "total_results": len(self.results),
                "algorithms": list({r.algorithm_name for r in self.results})
            },
            "tasks": [asdict(task) for task in self.tasks],
            "results": [asdict(result) for result in self.results],
            "summaries": {name: asdict(summary) for name, summary in summaries.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
    
    def _export_csv(self, output_path: Path):
        """Export results as CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if not self.results:
                return
            
            # Use the first result to determine fieldnames
            fieldnames = list(asdict(self.results[0]).keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.results:
                writer.writerow(asdict(result))
    
    def _export_html(self, output_path: Path):
        """Export results as HTML report."""
        summaries = self.generate_summary()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MassGen Algorithm Benchmark Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1, h2 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .algorithm {{ margin: 30px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
    </style>
</head>
<body>
    <h1>🧪 MassGen Algorithm Benchmark Report</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>Total Tasks: {len(self.tasks)}, Total Results: {len(self.results)}</p>
    
    <h2>📊 Algorithm Summaries</h2>
"""
        
        for algorithm_name, summary in summaries.items():
            html_content += f"""
    <div class="algorithm">
        <h3>{algorithm_name}</h3>
        <div class="metric">Success Rate: <strong class="{'success' if summary.success_rate > 0.8 else 'failure'}">{summary.success_rate:.1%}</strong></div>
        <div class="metric">Avg Duration: <strong>{summary.avg_duration:.1f}s</strong></div>
        <div class="metric">Consensus Rate: <strong>{summary.consensus_rate:.1%}</strong></div>
        {f'<div class="metric">Avg Correctness: <strong>{summary.avg_correctness:.2f}</strong></div>' if summary.avg_correctness else ''}
        {f'<div class="metric">Avg Quality: <strong>{summary.avg_quality:.2f}</strong></div>' if summary.avg_quality else ''}
    </div>
"""
        
        html_content += """
    <h2>📋 Detailed Results</h2>
    <table>
        <tr>
            <th>Algorithm</th>
            <th>Task ID</th>
            <th>Consensus</th>
            <th>Duration (s)</th>
            <th>Success Rate</th>
            <th>Status</th>
        </tr>
"""
        
        for result in self.results:
            status = "✅ Success" if not result.error else f"❌ {result.error[:50]}..."
            html_content += f"""
        <tr>
            <td>{result.algorithm_name}</td>
            <td>{result.task_id}</td>
            <td>{'Yes' if result.consensus_reached else 'No'}</td>
            <td>{result.session_duration:.1f}</td>
            <td>{result.success_rate:.1%}</td>
            <td>{status}</td>
        </tr>
"""
        
        html_content += """
    </table>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def print_summary(self):
        """Print a formatted summary to console."""
        summaries = self.generate_summary()
        
        print("\n" + "="*80)
        print("🧪 MASSGEN ALGORITHM BENCHMARK SUMMARY")
        print("="*80)
        
        if not summaries:
            print("❌ No benchmark results available")
            return
        
        for algorithm_name, summary in summaries.items():
            print(f"\n📊 {algorithm_name.upper()}")
            print("-" * 60)
            print(f"Success Rate:    {summary.success_rate:.1%} ({summary.successful_tasks}/{summary.total_tasks})")
            print(f"Avg Duration:    {summary.avg_duration:.2f}s (min: {summary.min_duration:.1f}s, max: {summary.max_duration:.1f}s)")
            print(f"Consensus Rate:  {summary.consensus_rate:.1%}")
            print(f"Avg Agents:      {summary.avg_agents_used:.1f}")
            print(f"Failure Rate:    {summary.avg_failure_rate:.1%}")
            
            if summary.avg_correctness is not None:
                print(f"Correctness:     {summary.avg_correctness:.3f}")
            if summary.avg_quality is not None:
                print(f"Quality:         {summary.avg_quality:.3f}")
            if summary.avg_efficiency is not None:
                print(f"Efficiency:      {summary.avg_efficiency:.3f}")
        
        print("\n" + "="*80)


# Default evaluators
def correctness_evaluator(task: BenchmarkTask, result: BenchmarkResult) -> float:
    """Simple correctness evaluator based on expected answer."""
    if not task.expected_answer:
        return 0.5  # No ground truth available
    
    answer_lower = result.answer.lower().strip()
    expected_lower = task.expected_answer.lower().strip()
    
    # Simple containment check
    if expected_lower in answer_lower:
        return 1.0
    elif any(word in answer_lower for word in expected_lower.split()):
        return 0.5
    else:
        return 0.0


def efficiency_evaluator(task: BenchmarkTask, result: BenchmarkResult) -> float:
    """Efficiency evaluator based on time and resource usage."""
    # Base efficiency on duration (lower is better)
    base_score = max(0.0, 1.0 - (result.session_duration / 300.0))  # 300s as baseline
    
    # Bonus for consensus and low failure rate
    consensus_bonus = 0.1 if result.consensus_reached else 0.0
    success_bonus = 0.1 * result.success_rate
    
    return min(1.0, base_score + consensus_bonus + success_bonus)


def quality_evaluator(task: BenchmarkTask, result: BenchmarkResult) -> float:
    """Quality evaluator based on answer characteristics."""
    answer = result.answer.strip()
    
    if not answer:
        return 0.0
    
    # Simple heuristics for quality
    score = 0.3  # Base score
    
    # Length indicates thoroughness
    if len(answer) > 100:
        score += 0.2
    if len(answer) > 500:
        score += 0.2
    
    # Structured reasoning indicators
    reasoning_indicators = ['because', 'therefore', 'analysis', 'evidence', 'conclusion']
    for indicator in reasoning_indicators:
        if indicator in answer.lower():
            score += 0.05
    
    # Consensus reached bonus
    if result.consensus_reached:
        score += 0.1
    
    return min(1.0, score)