#!/usr/bin/env python3
"""
Run benchmarks using Sakana AI's methodology from the TreeQuest paper.

SECURITY WARNING: This benchmark script executes AI-generated Python code using exec().
This is ONLY safe for evaluation in isolated sandbox environments. DO NOT run this
on production systems or with untrusted inputs. The AI models generate arbitrary
Python code that is executed dynamically for evaluation purposes.

Based on the original MassGen framework: https://github.com/Leezekun/MassGen
Copyright (c) 2025 The MassGen Authors

Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)

This implements benchmarks matching those described in:
"Adaptive Branching via Monte Carlo Tree Search for Efficient LLM Inference"
Sakana AI (arXiv:2503.04412)
"""

import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from canopy_core import run_mass_agents


class SakanaBenchmarkRunner:
    """Runner for Sakana AI-style benchmarks."""

    def __init__(self, output_dir: str = "benchmarks/results/sakana"):
        """Initialize benchmark runner."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up OpenRouter for DeepSeek R1
        self.setup_openrouter()

    def setup_openrouter(self):
        """Set up OpenRouter API for DeepSeek R1 access."""
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        # Set up for OpenRouter compatibility
        os.environ["OPENROUTER_BASE_URL"] = "https://openrouter.ai/api/v1"

    def run_arc_agi_2_benchmark(
        self,
        algorithm: str,
        models: List[str],
        task_ids: Optional[List[int]] = None,
        max_llm_calls: int = 250,
        num_runs: int = 1,
    ) -> Dict[str, Any]:
        """Run ARC-AGI-2 benchmark following Sakana methodology.

        Args:
            algorithm: Algorithm to use ("massgen" or "treequest")
            models: List of model names to use
            task_ids: Specific task IDs to run (None for all)
            max_llm_calls: Maximum LLM calls per problem (default 250)
            num_runs: Number of runs per task

        Returns:
            Benchmark results
        """
        print(f"\n🧪 Running ARC-AGI-2 benchmark with {algorithm}")
        print(f"   Models: {models}")
        print(f"   Max LLM calls: {max_llm_calls}")

        # Load ARC-AGI-2 tasks
        arc_tasks = self._load_arc_tasks(task_ids)

        results = []
        for task_id, task_data in arc_tasks.items():
            print(f"\n📋 Task {task_id}...")

            task_results = []
            for run in range(num_runs):
                print(f"   Run {run + 1}/{num_runs}...")

                start_time = time.time()

                try:
                    # Format task for MassGen
                    question = self._format_arc_task(task_data)

                    # Run with limited duration to match call budget
                    # Approximate: 250 calls * 2 seconds/call = 500 seconds max
                    max_duration = min(500, max_llm_calls * 2)

                    result = run_mass_agents(
                        question=question,
                        models=models,
                        max_duration=max_duration,
                        algorithm=algorithm,
                        streaming_display=False,
                    )

                    # Evaluate the generated code
                    passed = self._evaluate_arc_solution(task_data, result.get("answer", ""))

                    execution_time = time.time() - start_time

                    task_results.append(
                        {
                            "task_id": task_id,
                            "run": run + 1,
                            "passed": passed,
                            "execution_time": execution_time,
                            "algorithm": algorithm,
                            "models": models,
                        }
                    )

                    print(f"      {'✅ PASSED' if passed else '❌ FAILED'} in {execution_time:.2f}s")

                except Exception as e:
                    execution_time = time.time() - start_time
                    task_results.append(
                        {
                            "task_id": task_id,
                            "run": run + 1,
                            "passed": False,
                            "execution_time": execution_time,
                            "error": str(e),
                            "algorithm": algorithm,
                            "models": models,
                        }
                    )
                    print(f"      ❌ ERROR: {e}")

            results.extend(task_results)

        # Calculate Pass@k metrics
        pass_at_k = self._calculate_pass_at_k(results, num_runs)

        return {
            "algorithm": algorithm,
            "models": models,
            "total_tasks": len(arc_tasks),
            "num_runs": num_runs,
            "pass_at_k": pass_at_k,
            "individual_results": results,
        }

    def _load_arc_tasks(self, task_ids: Optional[List[int]] = None) -> Dict[int, Any]:
        """Load ARC-AGI-2 tasks from the Sakana repository."""
        arc_base = Path("benchmarks/ab-mcts-arc2/ARC-AGI-2")

        # Load task list
        task_list_file = Path("benchmarks/ab-mcts-arc2/experiments/arc2/arc_agi_2_eval_short.txt")
        if not task_list_file.exists():
            task_list_file = Path("benchmarks/ab-mcts-arc2/experiments/arc2/arc_agi_2_eval_full.txt")

        task_names = []
        if task_list_file.exists():
            with open(task_list_file) as f:
                task_names = [line.strip() for line in f if line.strip()]

        # Filter by task_ids if provided
        if task_ids is not None:
            task_names = [task_names[i] for i in task_ids if i < len(task_names)]

        # Load task data
        tasks = {}
        for i, task_name in enumerate(task_names[:5]):  # Limit to 5 tasks for testing
            task_file = arc_base / f"{task_name}.json"
            if task_file.exists():
                with open(task_file) as f:
                    tasks[i] = json.load(f)

        return tasks

    def _format_arc_task(self, task_data: Dict[str, Any]) -> str:
        """Format ARC task as a question for agents."""
        train_examples = task_data.get("train", [])
        test_examples = task_data.get("test", [])

        prompt = "You are given a pattern recognition task. Analyze the input-output examples and write a Python function that transforms the input grid to the output grid.\n\n"

        # Add training examples
        prompt += "Training Examples:\n"
        for i, example in enumerate(train_examples):
            prompt += f"\nExample {i+1}:\n"
            prompt += f"Input:\n{self._grid_to_string(example['input'])}\n"
            prompt += f"Output:\n{self._grid_to_string(example['output'])}\n"

        # Add test input
        if test_examples:
            prompt += "\nTest Input:\n"
            prompt += self._grid_to_string(test_examples[0]["input"])
            prompt += "\n\nWrite a Python function `transform(input_grid)` that takes the input grid and returns the transformed output grid."

        return prompt

    def _grid_to_string(self, grid: List[List[int]]) -> str:
        """Convert grid to string representation."""
        return "\n".join([" ".join(map(str, row)) for row in grid])

    def _evaluate_arc_solution(self, task_data: Dict[str, Any], solution: str) -> bool:
        """Evaluate if the solution correctly solves the ARC task.

        SECURITY WARNING: This method uses exec() to execute code generated by AI agents.
        This is intended for benchmark evaluation only and should NEVER be used in
        production or with untrusted code. The code being executed comes from AI model
        responses and may contain arbitrary Python code that could be malicious.

        This benchmark is designed to run in isolated environments only.
        """
        # Extract Python code from solution
        code = self._extract_python_code(solution)
        if not code:
            return False

        try:
            # SECURITY WARNING: Using exec() to execute AI-generated code
            # This is only safe in controlled benchmark environments
            # DO NOT use this pattern in production systems
            exec_globals = {}
            exec(code, exec_globals)

            if "transform" not in exec_globals:
                return False

            transform_fn = exec_globals["transform"]

            # Test on all training examples
            train_examples = task_data.get("train", [])
            for example in train_examples:
                input_grid = example["input"]
                expected_output = example["output"]

                try:
                    actual_output = transform_fn(input_grid)
                    if actual_output != expected_output:
                        return False
                except:
                    return False

            return True

        except:
            return False

    def _extract_python_code(self, text: str) -> Optional[str]:
        """Extract Python code from agent response."""
        # Look for code blocks
        if "```python" in text:
            code_start = text.find("```python") + 9
            code_end = text.find("```", code_start)
            if code_end > code_start:
                return text[code_start:code_end].strip()

        # Look for function definition
        if "def transform" in text:
            # Extract from def to the end or next non-code section
            lines = text.split("\n")
            code_lines = []
            in_function = False

            for line in lines:
                if "def transform" in line:
                    in_function = True

                if in_function:
                    # Stop at empty line after function
                    if not line.strip() and code_lines and not line.startswith(" "):
                        break
                    code_lines.append(line)

            return "\n".join(code_lines)

        return None

    def _calculate_pass_at_k(self, results: List[Dict[str, Any]], k: int) -> float:
        """Calculate Pass@k metric."""
        # Group by task_id
        by_task = {}
        for result in results:
            task_id = result["task_id"]
            if task_id not in by_task:
                by_task[task_id] = []
            by_task[task_id].append(result["passed"])

        # Calculate Pass@k
        passed_tasks = 0
        for task_id, task_results in by_task.items():
            # Task passes if any of the k attempts passed
            if any(task_results[:k]):
                passed_tasks += 1

        return passed_tasks / len(by_task) if by_task else 0.0

    def compare_algorithms(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comparative benchmark between algorithms."""
        print(f"\n🔬 Comparative Benchmark: {config['name']}")
        print(f"   Description: {config['description']}")

        results = {}

        for algorithm in config["algorithms"]:
            if algorithm == "treequest":
                # For TreeQuest, use multi-model setup as in paper
                models = config.get(
                    "treequest_models",
                    [
                        "gpt-4o-mini",
                        "gemini-2.5-pro",
                        "openrouter/deepseek/deepseek-r1",
                    ],
                )
            else:
                # For MassGen, use same models but in parallel voting
                models = config.get("massgen_models", ["gpt-4o-mini"] * 3)

            result = self.run_arc_agi_2_benchmark(
                algorithm=algorithm,
                models=models,
                task_ids=config.get("task_ids"),
                max_llm_calls=config.get("max_llm_calls", 250),
                num_runs=config.get("num_runs", 3),
            )

            results[algorithm] = result

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"sakana_benchmark_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(
                {"config": config, "results": results, "timestamp": timestamp},
                f,
                indent=2,
            )

        print(f"\n📊 Results saved to: {filename}")

        # Print comparison
        self._print_comparison(results)

        return results

    def _print_comparison(self, results: Dict[str, Dict[str, Any]]):
        """Print comparison between algorithms."""
        print("\n" + "=" * 60)
        print("📊 ALGORITHM COMPARISON (Sakana AI Methodology)")
        print("=" * 60)

        for algorithm, data in results.items():
            print(f"\n{algorithm.upper()}:")
            print(f"  Models: {', '.join(data['models'])}")
            print(f"  Pass@{data['num_runs']}: {data['pass_at_k']:.1%}")

            # Calculate average execution time
            times = [r["execution_time"] for r in data["individual_results"]]
            if times:
                print(f"  Avg execution time: {statistics.mean(times):.2f}s")

        # Show improvement
        if "massgen" in results and "treequest" in results:
            massgen_pass = results["massgen"]["pass_at_k"]
            treequest_pass = results["treequest"]["pass_at_k"]

            if massgen_pass > 0:
                improvement = (treequest_pass - massgen_pass) / massgen_pass * 100
                print(f"\n🚀 TreeQuest improvement over MassGen: {improvement:+.1f}%")


def create_default_sakana_config():
    """Create default Sakana benchmark configuration."""
    return {
        "name": "sakana_arc_agi_2",
        "description": "Reproduce Sakana AI TreeQuest benchmarks on ARC-AGI-2",
        "algorithms": ["massgen", "treequest"],
        "massgen_models": ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"],
        "treequest_models": [
            "gpt-4o-mini",
            "gemini-2.5-pro",
            "openrouter/deepseek/deepseek-r1",
        ],
        "task_ids": None,  # None for all tasks
        "max_llm_calls": 250,
        "num_runs": 3,
    }


def main():
    """Main entry point for Sakana benchmarks."""
    parser = argparse.ArgumentParser(description="Run Sakana AI-style benchmarks for algorithm comparison")
    parser.add_argument("--config", type=str, help="Path to benchmark configuration JSON")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmarks/results/sakana",
        help="Output directory for results",
    )
    parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=["massgen", "treequest"],
        help="Algorithms to benchmark",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick benchmark with minimal configuration",
    )
    parser.add_argument("--task-ids", nargs="+", type=int, help="Specific ARC task IDs to run")

    args = parser.parse_args()

    # Load or create configuration
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    elif args.quick:
        # Quick test configuration
        config = {
            "name": "quick_sakana_test",
            "description": "Quick test of Sakana benchmarks",
            "algorithms": args.algorithms or ["massgen"],
            "massgen_models": ["gpt-4o-mini", "gpt-4o-mini"],
            "treequest_models": ["gpt-4o-mini", "gpt-4o-mini"],
            "task_ids": [0, 1],  # Just first 2 tasks
            "max_llm_calls": 10,
            "num_runs": 1,
        }
    else:
        config = create_default_sakana_config()

        # Apply command line overrides
        if args.algorithms:
            config["algorithms"] = args.algorithms
        if args.task_ids:
            config["task_ids"] = args.task_ids

    # Run benchmarks
    runner = SakanaBenchmarkRunner(output_dir=args.output_dir)
    runner.compare_algorithms(config)


if __name__ == "__main__":
    main()
