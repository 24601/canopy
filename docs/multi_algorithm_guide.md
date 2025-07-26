# Multi-Algorithm Support and Benchmarking for MassGen

This document describes the multi-algorithm functionality and benchmarking framework added to MassGen.

## Overview

The MassGen system now supports multiple orchestration algorithms, enabling users to choose different approaches for multi-agent collaboration. Each algorithm implements the same interface but uses different strategies for agent coordination, consensus building, and task completion.

## Available Algorithms

### 1. Default Algorithm (`default`, `collaborative`)

The original MassGen collaborative algorithm that implements:
- Parallel agent execution with dynamic restarts
- Vote-based consensus mechanism
- Debate rounds for improved solutions
- Real-time collaboration through shared state

**Key Features:**
- Agents work in parallel and share updates
- Voting system for solution selection
- Automatic agent restart when others share new information
- Consensus-based decision making with debate fallback

**Best For:** General-purpose tasks requiring creative collaboration and diverse perspectives.

### 2. Arxiv 2503.04412 Inspired Algorithm (`arxiv_2503_04412`, `structured`)

A structured reasoning algorithm inspired by multi-agent reasoning approaches described in academic literature. This implementation follows common patterns found in research papers focused on systematic reasoning and evidence validation.

**Citation Note:** This algorithm is inspired by multi-agent reasoning methodologies commonly described in academic literature. The specific reference paper (https://arxiv.org/pdf/2503.04412) should be consulted for the exact methodology and properly cited in any academic or commercial use. The reference implementation can be found at https://github.com/SakanaAI/.

**Algorithm Phases:**
1. **Individual Reasoning**: Each agent independently analyzes the problem
2. **Critique Generation**: Agents provide structured critiques of others' reasoning
3. **Evidence Synthesis**: Agents incorporate feedback and refine solutions
4. **Consensus Validation**: Best solution selected based on evidence quality

**Key Features:**
- Structured reasoning phases instead of free-form collaboration
- Evidence-based solution evaluation
- Systematic critique and refinement process
- Quality scoring based on reasoning depth and evidence strength

**Best For:** Complex analytical tasks requiring systematic reasoning, logical consistency, and evidence validation.

## Configuration

### Algorithm Selection

Algorithms can be specified in three ways:

1. **Command Line:**
```bash
python cli.py "Your question" --models gpt-4o gemini-2.5-flash --algorithm arxiv_2503_04412
```

2. **YAML Configuration:**
```yaml
orchestrator:
  algorithm: structured
  max_duration: 600
  consensus_threshold: 0.7
  # Algorithm-specific parameters for Arxiv2503Algorithm
  max_reasoning_rounds: 2
  critique_rounds: 1
  evidence_threshold: 0.8
```

3. **Programmatic:**
```python
from massgen import create_config_from_models, run_mass_with_config

config = create_config_from_models(
    models=["gpt-4o", "gemini-2.5-flash"],
    orchestrator_config={
        "algorithm": "arxiv_2503_04412",
        "max_duration": 600,
        "evidence_threshold": 0.8
    }
)

result = run_mass_with_config("Your question", config)
```

### Algorithm-Specific Parameters

**DefaultAlgorithm:**
- `consensus_threshold`: Fraction of agents needed for consensus (0.0-1.0)
- `max_debate_rounds`: Maximum debate rounds before fallback
- `status_check_interval`: Agent status polling interval

**Arxiv2503Algorithm:**
- `evidence_threshold`: Minimum evidence score for consensus (0.0-1.0)
- `max_reasoning_rounds`: Maximum individual reasoning iterations
- `critique_rounds`: Number of critique generation rounds

## Benchmarking Framework

The benchmarking system allows comprehensive comparison of different algorithms across various tasks and metrics.

### Running Benchmarks

1. **Basic Comparison:**
```bash
python cli.py benchmark --algorithms default arxiv_2503_04412
```

2. **Custom Tasks:**
```bash
python cli.py benchmark --algorithms default structured --tasks my_tasks.json
```

3. **Export Results:**
```bash
python cli.py benchmark --algorithms default structured --export html --output-dir results/
```

### Benchmark Metrics

**Performance Metrics:**
- Success rate (tasks completed without errors)
- Average execution time
- Consensus achievement rate
- Agent failure rate

**Quality Metrics (when evaluators available):**
- Correctness score (0.0-1.0)
- Answer quality score (0.0-1.0)
- Efficiency score (0.0-1.0)

**Algorithm-Specific Metrics:**
- **Default**: Vote distribution, debate rounds
- **Arxiv2503**: Evidence scores, reasoning quality, critique depth

### Creating Custom Benchmark Tasks

Tasks are defined in JSON format:

```json
[
  {
    "task_id": "math_001",
    "question": "What is 15 * 23?",
    "category": "mathematics",
    "difficulty": "easy",
    "expected_answer": "345",
    "evaluation_criteria": ["numerical_accuracy"],
    "metadata": {
      "domain": "arithmetic",
      "requires_calculation": true
    }
  }
]
```

### Custom Evaluators

You can add custom evaluation functions:

```python
from massgen.benchmarking import BenchmarkSuite

def custom_evaluator(task, result):
    # Your evaluation logic
    return score  # 0.0 to 1.0

suite = BenchmarkSuite()
suite.add_evaluator("custom", custom_evaluator)
```

## Example Usage

### Algorithm Comparison

```python
from massgen import run_mass_with_config, create_config_from_models

question = "Analyze the economic impact of renewable energy adoption"

# Test with Default Algorithm
config1 = create_config_from_models(
    models=["gpt-4o", "gemini-2.5-flash"],
    orchestrator_config={"algorithm": "default"}
)
result1 = run_mass_with_config(question, config1)

# Test with Structured Reasoning Algorithm
config2 = create_config_from_models(
    models=["gpt-4o", "gemini-2.5-flash"],
    orchestrator_config={"algorithm": "arxiv_2503_04412"}
)
result2 = run_mass_with_config(question, config2)

print(f"Default Algorithm: {result1['session_duration']:.1f}s")
print(f"Structured Algorithm: {result2['session_duration']:.1f}s")
```

### Benchmarking

```python
from massgen.benchmarking import BenchmarkSuite, BenchmarkTask

# Create benchmark suite
suite = BenchmarkSuite()

# Add tasks
task = BenchmarkTask(
    task_id="analysis_001",
    question="Compare renewable vs fossil fuel energy",
    category="analysis", 
    difficulty="hard"
)
suite.add_task(task)

# Run benchmarks
results = suite.run_benchmark(
    algorithms=["default", "arxiv_2503_04412"],
    max_workers=2
)

# Generate report
suite.print_summary()
suite.export_results(format="html")
```

## Implementation Details

### Algorithm Interface

All algorithms inherit from the base `Algorithm` class:

```python
from massgen.algorithms.base import Algorithm

class CustomAlgorithm(Algorithm):
    def start_task(self, task):
        # Initialize and run algorithm
        return self._run_algorithm_workflow(task)
    
    def _run_algorithm_workflow(self, task):
        # Implement algorithm-specific logic
        return results
```

### Adding New Algorithms

1. Create algorithm class inheriting from `Algorithm`
2. Implement required methods: `start_task()`, `_run_algorithm_workflow()`
3. Register in `massgen/algorithms/__init__.py`
4. Add configuration validation if needed

### Compatibility

- All algorithms work with existing agents, streaming display, and logging
- UI remains fully functional regardless of algorithm choice
- Existing configurations continue to work (default algorithm used)
- Same agent types and models supported across all algorithms

## Best Practices

1. **Algorithm Selection:**
   - Use `default` for creative, collaborative tasks
   - Use `arxiv_2503_04412` for analytical, evidence-based tasks
   - Consider task complexity and available time

2. **Benchmarking:**
   - Use consistent model sets across algorithm comparisons
   - Include tasks of varying difficulty and categories
   - Run multiple iterations for statistical significance

3. **Configuration:**
   - Adjust algorithm-specific parameters based on task requirements
   - Consider timeout settings for complex algorithms
   - Use appropriate consensus thresholds

## Academic Citation

When using the Arxiv 2503.04412 inspired algorithm in academic work, please include appropriate citations to the original research. The algorithm implementation is inspired by multi-agent reasoning methodologies described in academic literature, with the specific reference paper being https://arxiv.org/pdf/2503.04412. The reference implementation from SakanaAI (https://github.com/SakanaAI/) should also be acknowledged.

**Note**: This implementation represents an interpretation of academic multi-agent reasoning approaches and may differ from the exact methodology described in the original paper. Users should consult the original research for precise algorithmic details.

## Future Extensions

The algorithm framework is designed for easy extension:

- New orchestration strategies can be added as algorithm classes
- Benchmarking supports custom metrics and evaluators  
- Configuration system allows algorithm-specific parameters
- UI and logging work seamlessly with any algorithm implementation

This multi-algorithm approach enables researchers and practitioners to choose the most appropriate orchestration strategy for their specific use cases while maintaining full system compatibility and functionality.