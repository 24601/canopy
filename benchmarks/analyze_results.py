#!/usr/bin/env python3
"""
Analyze and visualize benchmark results.

Based on the original MassGen framework: https://github.com/Leezekun/MassGen
Copyright (c) 2025 The MassGen Authors

Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601)

This file is part of the extended framework (canopy) for comparing orchestration algorithms.
"""

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class BenchmarkAnalyzer:
    """Analyzer for benchmark results."""

    def __init__(self, results_dir: str = "benchmarks/results"):
        """Initialize analyzer."""
        self.results_dir = Path(results_dir)

    def load_results(self, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """Load all benchmark results matching pattern."""
        results = []

        for file_path in self.results_dir.glob(pattern):
            with open(file_path) as f:
                data = json.load(f)
                results.append(data)

        return results

    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze benchmark results and generate statistics."""
        analysis = {
            "total_files": len(results),
            "algorithms": {},
            "by_agent_count": {},
            "by_question_complexity": {},
            "consensus_analysis": {},
        }

        # Aggregate all individual results
        all_results = []
        for file_data in results:
            all_results.extend(file_data["results"])

        # Analyze by algorithm
        by_algorithm = defaultdict(list)
        for result in all_results:
            if result.get("success_rate", 0) > 0:
                by_algorithm[result["algorithm"]].append(result)

        for algo, algo_results in by_algorithm.items():
            analysis["algorithms"][algo] = self._analyze_algorithm(algo_results)

        # Analyze by agent count
        by_agents = defaultdict(lambda: defaultdict(list))
        for result in all_results:
            if result.get("success_rate", 0) > 0:
                n_agents = result["num_agents"]
                algo = result["algorithm"]
                by_agents[n_agents][algo].append(result)

        for n_agents, algo_data in by_agents.items():
            analysis["by_agent_count"][n_agents] = {}
            for algo, results in algo_data.items():
                analysis["by_agent_count"][n_agents][algo] = self._analyze_algorithm(results)

        # Analyze consensus patterns
        for algo, algo_results in by_algorithm.items():
            consensus_data = []
            for result in algo_results:
                if "consensus_rate" in result:
                    consensus_data.append(
                        {
                            "rate": result["consensus_rate"],
                            "debate_rounds": result.get("avg_debate_rounds", 0),
                            "execution_time": result["avg_execution_time"],
                        }
                    )

            if consensus_data:
                analysis["consensus_analysis"][algo] = {
                    "avg_consensus_rate": statistics.mean([d["rate"] for d in consensus_data]),
                    "avg_debate_rounds": statistics.mean([d["debate_rounds"] for d in consensus_data]),
                    "correlation_time_consensus": self._calculate_correlation(
                        [d["execution_time"] for d in consensus_data], [d["rate"] for d in consensus_data]
                    ),
                }

        return analysis

    def _analyze_algorithm(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze results for a single algorithm."""
        exec_times = []
        consensus_rates = []
        debate_rounds = []

        for result in results:
            exec_times.append(result["avg_execution_time"])
            if "consensus_rate" in result:
                consensus_rates.append(result["consensus_rate"])
            if "avg_debate_rounds" in result:
                debate_rounds.append(result["avg_debate_rounds"])

        analysis = {
            "num_benchmarks": len(results),
            "execution_time": {
                "mean": statistics.mean(exec_times),
                "std": statistics.stdev(exec_times) if len(exec_times) > 1 else 0,
                "min": min(exec_times),
                "max": max(exec_times),
                "median": statistics.median(exec_times),
            },
        }

        if consensus_rates:
            analysis["consensus"] = {
                "mean": statistics.mean(consensus_rates),
                "std": statistics.stdev(consensus_rates) if len(consensus_rates) > 1 else 0,
                "min": min(consensus_rates),
                "max": max(consensus_rates),
            }

        if debate_rounds:
            analysis["debate_rounds"] = {
                "mean": statistics.mean(debate_rounds),
                "std": statistics.stdev(debate_rounds) if len(debate_rounds) > 1 else 0,
                "min": min(debate_rounds),
                "max": max(debate_rounds),
            }

        return analysis

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        sum_y2 = sum(yi**2 for yi in y)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)) ** 0.5

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a formatted report from analysis."""
        report = []

        report.append("# MassGen Algorithm Benchmark Analysis Report")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total benchmark files analyzed: {analysis['total_files']}")

        # Algorithm comparison
        report.append("\n## Algorithm Performance Comparison")

        for algo, data in analysis["algorithms"].items():
            report.append(f"\n### {algo.upper()}")
            report.append(f"- Benchmarks run: {data['num_benchmarks']}")

            exec_time = data["execution_time"]
            report.append(f"- Execution time:")
            report.append(f"  - Mean: {exec_time['mean']:.2f}s (± {exec_time['std']:.2f}s)")
            report.append(f"  - Median: {exec_time['median']:.2f}s")
            report.append(f"  - Range: [{exec_time['min']:.2f}s, {exec_time['max']:.2f}s]")

            if "consensus" in data:
                consensus = data["consensus"]
                report.append(f"- Consensus rate:")
                report.append(f"  - Mean: {consensus['mean']:.1%} (± {consensus['std']:.1%})")
                report.append(f"  - Range: [{consensus['min']:.1%}, {consensus['max']:.1%}]")

            if "debate_rounds" in data:
                debate = data["debate_rounds"]
                report.append(f"- Debate rounds:")
                report.append(f"  - Mean: {debate['mean']:.1f} (± {debate['std']:.1f})")

        # Performance by agent count
        report.append("\n## Performance by Agent Count")

        for n_agents in sorted(analysis["by_agent_count"].keys()):
            report.append(f"\n### {n_agents} Agents")

            algo_data = analysis["by_agent_count"][n_agents]
            if len(algo_data) > 1:
                # Compare algorithms
                fastest = min(algo_data.items(), key=lambda x: x[1]["execution_time"]["mean"])
                report.append(f"- Fastest: {fastest[0]} ({fastest[1]['execution_time']['mean']:.2f}s)")

                for algo, data in algo_data.items():
                    report.append(f"- {algo}: {data['execution_time']['mean']:.2f}s")
            else:
                # Single algorithm
                for algo, data in algo_data.items():
                    report.append(f"- {algo}: {data['execution_time']['mean']:.2f}s")

        # Consensus analysis
        if analysis["consensus_analysis"]:
            report.append("\n## Consensus Analysis")

            for algo, data in analysis["consensus_analysis"].items():
                report.append(f"\n### {algo.upper()}")
                report.append(f"- Average consensus rate: {data['avg_consensus_rate']:.1%}")
                report.append(f"- Average debate rounds: {data['avg_debate_rounds']:.1f}")
                report.append(f"- Time-consensus correlation: {data['correlation_time_consensus']:.2f}")

        # Recommendations
        report.append("\n## Recommendations")

        # Find best algorithm for speed
        if len(analysis["algorithms"]) > 1:
            fastest_algo = min(analysis["algorithms"].items(), key=lambda x: x[1]["execution_time"]["mean"])
            report.append(
                f"\n- **Fastest algorithm**: {fastest_algo[0]} "
                f"(avg: {fastest_algo[1]['execution_time']['mean']:.2f}s)"
            )

        # Find best algorithm for consensus
        consensus_algos = [
            (algo, data["consensus"]["mean"]) for algo, data in analysis["algorithms"].items() if "consensus" in data
        ]
        if consensus_algos:
            best_consensus = max(consensus_algos, key=lambda x: x[1])
            report.append(f"- **Best consensus rate**: {best_consensus[0]} " f"({best_consensus[1]:.1%})")

        return "\n".join(report)

    def save_report(self, report: str, filename: str = None):
        """Save report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_analysis_{timestamp}.md"

        output_path = self.results_dir / filename
        with open(output_path, "w") as f:
            f.write(report)

        print(f"📄 Report saved to: {output_path}")
        return output_path


def main():
    """Main entry point for analysis."""
    parser = argparse.ArgumentParser(description="Analyze MassGen benchmark results")
    parser.add_argument(
        "--results-dir", type=str, default="benchmarks/results", help="Directory containing benchmark results"
    )
    parser.add_argument("--pattern", type=str, default="*.json", help="File pattern to match")
    parser.add_argument("--output", type=str, help="Output file for report")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = BenchmarkAnalyzer(results_dir=args.results_dir)

    # Load results
    print(f"📂 Loading results from: {args.results_dir}")
    results = analyzer.load_results(pattern=args.pattern)

    if not results:
        print("❌ No benchmark results found!")
        return

    print(f"✅ Loaded {len(results)} benchmark files")

    # Analyze results
    print("🔍 Analyzing results...")
    analysis = analyzer.analyze_results(results)

    # Generate report
    print("📝 Generating report...")
    report = analyzer.generate_report(analysis)

    # Save report
    analyzer.save_report(report, filename=args.output)

    # Print summary to console
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for algo, data in analysis["algorithms"].items():
        print(f"\n{algo.upper()}:")
        print(f"  Mean execution time: {data['execution_time']['mean']:.2f}s")
        if "consensus" in data:
            print(f"  Mean consensus rate: {data['consensus']['mean']:.1%}")


if __name__ == "__main__":
    main()
