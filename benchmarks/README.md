# Canopy Benchmarking Suite

This directory contains Canopy's comprehensive benchmarking framework for evaluating multi-agent algorithm performance.

## 📁 Structure

```
benchmarks/
├── README.md                 # This file
├── run_benchmarks.py        # General algorithm comparison framework
├── sakana_benchmarks.py     # ARC-AGI-2 benchmarks (Sakana AI methodology)
├── analyze_results.py       # Statistical analysis and visualization
├── configs/                 # Benchmark configuration files
│   ├── default.yaml
│   ├── arc_agi_2.yaml
│   └── quick_test.yaml
├── results/                 # Benchmark results (gitignored)
└── ab-mcts-arc2/           # External Sakana AI benchmark repo (gitignored)
```

## 🚀 Quick Start

### Basic Algorithm Comparison

```bash
# Run default benchmark suite
python benchmarks/run_benchmarks.py

# Quick test (faster, smaller scale)
python benchmarks/run_benchmarks.py --quick

# Compare specific algorithms
python benchmarks/run_benchmarks.py --algorithms massgen treequest
```

### ARC-AGI-2 Benchmarks

**Note**: ARC-AGI-2 benchmarks require the external Sakana AI dataset.

```bash
# 1. Clone the external benchmark repository
git clone https://github.com/SakanaAI/ab-mcts-arc2.git benchmarks/ab-mcts-arc2

# 2. Install additional dependencies
cd benchmarks/ab-mcts-arc2
uv sync  # or pip install -r requirements.txt

# 3. Run ARC-AGI-2 benchmarks
cd ../..
python benchmarks/sakana_benchmarks.py

# Quick test with limited tasks
python benchmarks/sakana_benchmarks.py --quick
```

## 📊 Benchmark Types

### 1. Algorithm Comparison (`run_benchmarks.py`)

**Purpose**: Compare different multi-agent orchestration algorithms

**Metrics**:
- Execution time
- Consensus rate
- Success rate
- Scalability with agent count

**Usage**:
```bash
python benchmarks/run_benchmarks.py --config configs/algorithm_comparison.yaml
```

### 2. ARC-AGI-2 Evaluation (`sakana_benchmarks.py`)

**Purpose**: Evaluate on Abstract Reasoning Corpus tasks following Sakana AI methodology

**Based on**: [Adaptive Branching via Monte Carlo Tree Search for Efficient LLM Inference](https://arxiv.org/abs/2503.04412)

**Metrics**:
- Pass@k accuracy
- Pattern recognition performance
- Code generation quality
- LLM call efficiency

**Usage**:
```bash
python benchmarks/sakana_benchmarks.py --config configs/arc_agi_2.yaml
```

## 🔧 Configuration

### Example Configuration

```yaml
# configs/my_benchmark.yaml
name: "custom_evaluation"
description: "Custom algorithm evaluation"

benchmarks:
  - name: "reasoning_tasks"
    questions:
      - "Explain quantum mechanics simply"
      - "Design a sustainable city"
    
    models: ["gpt-4o", "claude-3-sonnet"]
    algorithms: ["massgen", "treequest"]
    num_runs: 3
    max_duration: 120
```

### Usage with Custom Config

```bash
python benchmarks/run_benchmarks.py --config configs/my_benchmark.yaml
```

## 📈 Example Results

### Algorithm Performance Comparison

| Algorithm | Pass@3 (ARC-AGI-2) | Avg Time | Consensus Rate |
|-----------|--------------------:|---------:|---------------:|
| TreeQuest | 23.5% | 45.2s | 78% |
| MassGen | 18.1% | 38.7s | 82% |
| Single | 12.3% | 28.1s | N/A |

### Scaling Performance

| Agents | TreeQuest Time | MassGen Time | TreeQuest Accuracy |
|--------|---------------:|-------------:|-------------------:|
| 2 | 32.1s | 28.4s | 18.2% |
| 3 | 45.2s | 38.7s | 23.5% |
| 4 | 61.8s | 52.3s | 26.1% |

## 🔍 Analysis Tools

### Statistical Analysis

```bash
# Generate comprehensive report
python benchmarks/analyze_results.py --results benchmarks/results/

# Statistical significance testing
python benchmarks/analyze_results.py --significance-test --alpha 0.05

# Generate plots
python benchmarks/analyze_results.py --plot-type comparison --save-plots
```

### Custom Analysis

```python
from benchmarks.analyze_results import ResultAnalyzer

analyzer = ResultAnalyzer()
results = analyzer.load_results("benchmarks/results/")
stats = analyzer.compute_statistics(results)

print(f"TreeQuest improvement: {stats['treequest_improvement']:.1%}")
```

## 🏗️ Adding Custom Benchmarks

### 1. Create Benchmark Class

```python
class MyCustomBenchmark:
    def __init__(self, config):
        self.config = config
    
    def run_evaluation(self, algorithm, models):
        # Implement evaluation logic
        pass
    
    def compute_metrics(self, results):
        # Return standardized metrics
        pass
```

### 2. Add to Framework

```python
# In run_benchmarks.py
from my_benchmark import MyCustomBenchmark

# Register benchmark
BENCHMARK_REGISTRY["my_benchmark"] = MyCustomBenchmark
```

## ⚠️ External Dependencies

### ARC-AGI-2 Benchmark Repository

The ARC-AGI-2 benchmarks require the external Sakana AI repository:

- **Repository**: https://github.com/SakanaAI/ab-mcts-arc2
- **Purpose**: Provides ARC-AGI-2 dataset and evaluation framework
- **License**: Apache 2.0
- **Setup**: Manual clone required (see instructions above)

**Why not included**:
- Large repository (~50MB with datasets)
- External dependency with its own development cycle
- Only needed for specific ARC-AGI-2 benchmarks
- Keeps our core repository lightweight

### Installation Script

```bash
#!/bin/bash
# setup_benchmarks.sh
echo "Setting up Canopy benchmarking..."

# Clone external benchmark repo
if [ ! -d "benchmarks/ab-mcts-arc2" ]; then
    echo "Cloning ARC-AGI-2 benchmark repository..."
    git clone https://github.com/SakanaAI/ab-mcts-arc2.git benchmarks/ab-mcts-arc2
fi

# Install dependencies
cd benchmarks/ab-mcts-arc2
echo "Installing ARC-AGI-2 dependencies..."
uv sync || pip install -r requirements.txt

echo "✅ Benchmark setup complete!"
```

## 🤝 Contributing

We welcome benchmark contributions! Please:

1. Follow our configuration format
2. Include baseline results
3. Document thoroughly
4. Ensure reproducibility

## 📚 Further Reading

- **[Full Benchmarking Guide](../docs/benchmarking.md)** - Comprehensive documentation
- **[TreeQuest Paper](https://arxiv.org/abs/2503.04412)** - Original algorithm description
- **[ARC-AGI-2 Dataset](https://github.com/arcprize/ARC-AGI-2)** - Pattern recognition benchmark
- **[Results Archive](results/)** - Historical performance data

---

For questions about benchmarking, please check our [FAQ](../docs/faq.md) or [open an issue](https://github.com/yourusername/canopy/issues).