#!/usr/bin/env python3
"""
Run benchmarks comparing different orchestration algorithms.

Based on the original MassGen framework: https://github.com/Leezekun/MassGen
Copyright (c) 2025 The MassGen Authors

Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)

This file is part of the extended framework (canopy) for comparing orchestration algorithms.
"""

import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from massgen import run_mass_agents


class BenchmarkRunner:
    """Runner for algorithm benchmarks."""

    def __init__(self, output_dir: str = "benchmarks/results"):
        """Initialize benchmark runner."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []

    def run_single_benchmark(
        self,
        algorithm: str,
        question: str,
        models: List[str],
        max_duration: int = 60,
        consensus_threshold: float = 0.5,
        num_runs: int = 3,
    ) -> Dict[str, Any]:
        """Run a single benchmark configuration multiple times."""
        print(f"\n🔬 Benchmarking {algorithm} with {len(models)} agents...")
        print(f"   Question: {question[:50]}...")
        print(f"   Models: {models}")
        print(f"   Runs: {num_runs}")

        run_results = []

        for run in range(num_runs):
            print(f"\n   Run {run + 1}/{num_runs}...")

            start_time = time.time()

            try:
                result = run_mass_agents(
                    question=question,
                    models=models,
                    max_duration=max_duration,
                    consensus_threshold=consensus_threshold,
                    algorithm=algorithm,
                    streaming_display=False,  # Disable display for benchmarks
                )

                execution_time = time.time() - start_time

                run_results.append(
                    {
                        "run": run + 1,
                        "success": True,
                        "execution_time": execution_time,
                        "consensus_reached": result.get("consensus_reached", False),
                        "debate_rounds": result.get("debate_rounds", 0),
                        "answer_length": len(result.get("answer", "")),
                    }
                )

                print(f"      ✅ Completed in {execution_time:.2f}s")

            except Exception as e:
                execution_time = time.time() - start_time
                run_results.append(
                    {"run": run + 1, "success": False, "execution_time": execution_time, "error": str(e)}
                )
                print(f"      ❌ Failed: {e}")

        # Calculate statistics
        successful_runs = [r for r in run_results if r["success"]]

        if successful_runs:
            exec_times = [r["execution_time"] for r in successful_runs]
            consensus_rates = [1 if r["consensus_reached"] else 0 for r in successful_runs]
            debate_rounds = [r["debate_rounds"] for r in successful_runs]

            stats = {
                "algorithm": algorithm,
                "question": question,
                "models": models,
                "num_agents": len(models),
                "num_runs": num_runs,
                "success_rate": len(successful_runs) / num_runs,
                "avg_execution_time": statistics.mean(exec_times),
                "std_execution_time": statistics.stdev(exec_times) if len(exec_times) > 1 else 0,
                "min_execution_time": min(exec_times),
                "max_execution_time": max(exec_times),
                "consensus_rate": statistics.mean(consensus_rates),
                "avg_debate_rounds": statistics.mean(debate_rounds),
                "individual_runs": run_results,
            }
        else:
            stats = {
                "algorithm": algorithm,
                "question": question,
                "models": models,
                "num_agents": len(models),
                "num_runs": num_runs,
                "success_rate": 0,
                "error": "All runs failed",
                "individual_runs": run_results,
            }

        return stats

    def run_benchmark_suite(self, config: Dict[str, Any]):
        """Run a suite of benchmarks based on configuration."""
        print(f"\n🚀 Starting Benchmark Suite: {config['name']}")
        print(f"   Description: {config['description']}")

        results = []

        for benchmark in config["benchmarks"]:
            for algorithm in benchmark["algorithms"]:
                result = self.run_single_benchmark(
                    algorithm=algorithm,
                    question=benchmark["question"],
                    models=benchmark["models"],
                    max_duration=benchmark.get("max_duration", 60),
                    consensus_threshold=benchmark.get("consensus_threshold", 0.5),
                    num_runs=benchmark.get("num_runs", 3),
                )
                results.append(result)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"benchmark_{config['name']}_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump({"suite": config, "results": results, "timestamp": timestamp}, f, indent=2)

        print(f"\n📊 Results saved to: {filename}")

        # Print summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: List[Dict[str, Any]]):
        """Print a summary of benchmark results."""
        print("\n" + "=" * 60)
        print("📈 BENCHMARK SUMMARY")
        print("=" * 60)

        # Group by algorithm
        by_algorithm = {}
        for result in results:
            algo = result["algorithm"]
            if algo not in by_algorithm:
                by_algorithm[algo] = []
            if result.get("success_rate", 0) > 0:
                by_algorithm[algo].append(result)

        for algo, algo_results in by_algorithm.items():
            if not algo_results:
                print(f"\n{algo.upper()}: No successful runs")
                continue

            print(f"\n{algo.upper()}:")

            # Average across all benchmarks
            avg_time = statistics.mean([r["avg_execution_time"] for r in algo_results])
            avg_consensus = statistics.mean([r["consensus_rate"] for r in algo_results])
            avg_success = statistics.mean([r["success_rate"] for r in algo_results])

            print(f"  Average execution time: {avg_time:.2f}s")
            print(f"  Average consensus rate: {avg_consensus:.1%}")
            print(f"  Average success rate: {avg_success:.1%}")

            # By number of agents
            by_agents = {}
            for r in algo_results:
                n = r["num_agents"]
                if n not in by_agents:
                    by_agents[n] = []
                by_agents[n].append(r["avg_execution_time"])

            print(f"  By agent count:")
            for n in sorted(by_agents.keys()):
                avg = statistics.mean(by_agents[n])
                print(f"    {n} agents: {avg:.2f}s")


def create_default_benchmark_config():
    """Create default benchmark configuration."""
    return {
        "name": "algorithm_comparison",
        "description": "Compare MassGen and TreeQuest algorithms",
        "benchmarks": [
            # Simple task with 2 agents
            {
                "question": "What is the capital of France?",
                "models": ["gpt-4o-mini", "gpt-4o-mini"],
                "algorithms": ["massgen", "treequest"],
                "num_runs": 3,
            },
            # Medium complexity with 3 agents
            {
                "question": "Explain the concept of quantum entanglement in simple terms.",
                "models": ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"],
                "algorithms": ["massgen", "treequest"],
                "num_runs": 3,
            },
            # Complex task with 4 agents
            {
                "question": "Design a sustainable city infrastructure for a population of 1 million.",
                "models": ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"],
                "algorithms": ["massgen", "treequest"],
                "num_runs": 2,
                "max_duration": 120,
            },
            # Consensus testing with different thresholds
            {
                "question": "Should artificial intelligence be regulated by governments?",
                "models": ["gpt-4o-mini", "gpt-4o-mini", "gpt-4o-mini"],
                "algorithms": ["massgen", "treequest"],
                "consensus_threshold": 0.7,
                "num_runs": 3,
            },
        ],
    }


def main():
    """Main benchmark entry point."""
    parser = argparse.ArgumentParser(description="Run MassGen algorithm benchmarks")
    parser.add_argument("--config", type=str, help="Path to benchmark configuration JSON")
    parser.add_argument("--output-dir", type=str, default="benchmarks/results", help="Output directory for results")
    parser.add_argument("--algorithms", nargs="+", choices=["massgen", "treequest"], help="Algorithms to benchmark")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark with minimal configuration")

    args = parser.parse_args()

    # Load or create configuration
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    elif args.quick:
        # Quick benchmark for testing
        config = {
            "name": "quick_test",
            "description": "Quick algorithm comparison",
            "benchmarks": [
                {
                    "question": "What is 2+2?",
                    "models": ["gpt-4o-mini", "gpt-4o-mini"],
                    "algorithms": args.algorithms or ["massgen", "treequest"],
                    "num_runs": 1,
                }
            ],
        }
    else:
        config = create_default_benchmark_config()

        # Filter algorithms if specified
        if args.algorithms:
            for benchmark in config["benchmarks"]:
                benchmark["algorithms"] = [a for a in benchmark["algorithms"] if a in args.algorithms]

    # Run benchmarks
    runner = BenchmarkRunner(output_dir=args.output_dir)
    runner.run_benchmark_suite(config)


if __name__ == "__main__":
    main()
