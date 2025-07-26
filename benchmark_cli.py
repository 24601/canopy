#!/usr/bin/env python3
"""
MassGen Benchmarking CLI

Command-line interface for running benchmarks on different MassGen algorithms.
This tool allows users to compare algorithm performance across various tasks.

Usage examples:
    # Run benchmarks on default tasks
    python benchmark_cli.py --algorithms default arxiv_2503_04412
    
    # Run with custom task file
    python benchmark_cli.py --algorithms default structured --tasks benchmark_tasks.json
    
    # Export results in different formats
    python benchmark_cli.py --algorithms default --export html --output my_results.html
    
    # Run with specific configuration
    python benchmark_cli.py --algorithms arxiv_2503_04412 --max-duration 600 --models gpt-4o gemini-2.5-flash
"""

import argparse
import sys
import json
from pathlib import Path

# Add massgen package to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main CLI function for benchmarking."""
    parser = argparse.ArgumentParser(
        description="MassGen Algorithm Benchmarking Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic benchmark comparison
  python benchmark_cli.py --algorithms default arxiv_2503_04412
  
  # Custom configuration
  python benchmark_cli.py --algorithms structured --max-duration 600
  
  # Export results
  python benchmark_cli.py --algorithms default structured --export html
        """
    )
    
    # Algorithm selection
    parser.add_argument("--algorithms", nargs="+", required=True,
                       help="Algorithms to benchmark (default, arxiv_2503_04412, structured)")
    
    # Task configuration
    parser.add_argument("--tasks", type=str, 
                       help="JSON file containing benchmark tasks (uses default tasks if not provided)")
    parser.add_argument("--categories", nargs="+", 
                       help="Filter tasks by categories (mathematics, logic, reasoning, analysis, creativity)")
    parser.add_argument("--difficulty", choices=["easy", "medium", "hard"], 
                       help="Filter tasks by difficulty level")
    
    # Algorithm configuration
    parser.add_argument("--models", nargs="+", default=["gpt-4o", "gemini-2.5-flash"],
                       help="Models to use for benchmarking")
    parser.add_argument("--max-duration", type=int, default=300,
                       help="Maximum duration per task in seconds")
    parser.add_argument("--max-workers", type=int, default=2,
                       help="Maximum concurrent benchmark workers")
    
    # Output configuration
    parser.add_argument("--export", choices=["json", "csv", "html"], default="json",
                       help="Export format for results")
    parser.add_argument("--output", type=str,
                       help="Output filename (auto-generated if not provided)")
    parser.add_argument("--output-dir", type=str, default="benchmark_results",
                       help="Output directory for results")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress verbose output")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Import benchmarking components
        from massgen.benchmarking import BenchmarkSuite, BenchmarkTask, correctness_evaluator, efficiency_evaluator, quality_evaluator
        from massgen.algorithms import get_available_algorithms
        
        # Validate algorithms
        available_algorithms = get_available_algorithms()
        for algorithm in args.algorithms:
            if algorithm not in available_algorithms:
                print(f"❌ Error: Unknown algorithm '{algorithm}'")
                print(f"Available algorithms: {available_algorithms}")
                sys.exit(1)
        
        if not args.quiet:
            print("🧪 MassGen Algorithm Benchmarking Tool")
            print("="*60)
            print(f"Algorithms: {args.algorithms}")
            print(f"Models: {args.models}")
            print(f"Max duration: {args.max_duration}s")
            print(f"Export format: {args.export}")
            print("="*60)
        
        # Initialize benchmark suite
        suite = BenchmarkSuite(output_dir=args.output_dir)
        
        # Add evaluators
        suite.add_evaluator("correctness", correctness_evaluator)
        suite.add_evaluator("efficiency", efficiency_evaluator)
        suite.add_evaluator("quality", quality_evaluator)
        
        # Load or create tasks
        if args.tasks:
            if not Path(args.tasks).exists():
                print(f"❌ Error: Task file not found: {args.tasks}")
                sys.exit(1)
            suite.add_tasks_from_file(args.tasks)
        else:
            suite.create_default_tasks()
        
        # Filter tasks if requested
        if args.categories:
            suite.tasks = [t for t in suite.tasks if t.category in args.categories]
        if args.difficulty:
            suite.tasks = [t for t in suite.tasks if t.difficulty == args.difficulty]
        
        if not suite.tasks:
            print("❌ Error: No tasks match the specified criteria")
            sys.exit(1)
        
        if not args.quiet:
            print(f"📋 Running {len(suite.tasks)} tasks")
        
        # Prepare configuration template
        config_template = {
            "max_duration": args.max_duration,
        }
        
        # Run benchmarks
        print("🚀 Starting benchmark execution...")
        results = suite.run_benchmark(
            algorithms=args.algorithms,
            config_template=config_template,
            max_workers=args.max_workers,
            timeout_per_task=args.max_duration
        )
        
        # Print summary
        if not args.quiet:
            suite.print_summary()
        
        # Export results
        output_file = suite.export_results(format=args.export, filename=args.output)
        print(f"📁 Results exported to: {output_file}")
        
        # Print quick comparison
        summaries = suite.generate_summary()
        if len(summaries) > 1:
            print("\n🏆 Quick Comparison:")
            best_success = max(summaries.values(), key=lambda s: s.success_rate)
            best_speed = min(summaries.values(), key=lambda s: s.avg_duration)
            best_consensus = max(summaries.values(), key=lambda s: s.consensus_rate)
            
            print(f"Best Success Rate: {best_success.algorithm_name} ({best_success.success_rate:.1%})")
            print(f"Fastest Average:   {best_speed.algorithm_name} ({best_speed.avg_duration:.1f}s)")
            print(f"Best Consensus:    {best_consensus.algorithm_name} ({best_consensus.consensus_rate:.1%})")
        
        print("\n✅ Benchmarking completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure MassGen dependencies are installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Benchmarking interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()