#!/bin/bash
# Setup script for Canopy benchmarking suite
# This script sets up external dependencies needed for comprehensive benchmarking

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "🧪 Canopy Benchmarking Setup"
echo "============================"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "benchmarks/run_benchmarks.py" ]; then
    echo -e "${RED}Error: Please run this script from the Canopy root directory${NC}"
    exit 1
fi

# Create results directories
echo -e "${BLUE}Creating benchmark result directories...${NC}"
mkdir -p benchmarks/results/general
mkdir -p benchmarks/results/sakana
mkdir -p benchmarks/configs

# Check for ARC-AGI-2 benchmark repository
echo -e "${BLUE}Checking for ARC-AGI-2 benchmark repository...${NC}"

if [ ! -d "benchmarks/ab-mcts-arc2" ]; then
    echo -e "${YELLOW}ARC-AGI-2 benchmark repository not found.${NC}"
    echo -e "This is required for running Sakana AI-style benchmarks on the ARC-AGI-2 dataset."
    echo -e "\nRepository: ${BLUE}https://github.com/SakanaAI/ab-mcts-arc2${NC}"
    echo -e "License: Apache 2.0"
    echo -e "Size: ~50MB (includes datasets)"

    read -p "$(echo -e ${YELLOW}Download ARC-AGI-2 benchmark repository? [y/N]: ${NC})" -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Cloning ARC-AGI-2 benchmark repository...${NC}"
        git clone --depth 1 https://github.com/SakanaAI/ab-mcts-arc2.git benchmarks/ab-mcts-arc2

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ ARC-AGI-2 repository cloned successfully${NC}"
        else
            echo -e "${RED}✗ Failed to clone ARC-AGI-2 repository${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Skipping ARC-AGI-2 setup. Sakana benchmarks will not be available.${NC}"
        echo -e "You can run: git clone https://github.com/SakanaAI/ab-mcts-arc2.git benchmarks/ab-mcts-arc2"
        ARC_SKIPPED=true
    fi
else
    echo -e "${GREEN}✓ ARC-AGI-2 repository found${NC}"
fi

# Install ARC-AGI-2 dependencies if repository exists
if [ -d "benchmarks/ab-mcts-arc2" ] && [ "$ARC_SKIPPED" != "true" ]; then
    echo -e "${BLUE}Installing ARC-AGI-2 dependencies...${NC}"

    cd benchmarks/ab-mcts-arc2

    # Check for uv first, then pip
    if command -v uv >/dev/null 2>&1; then
        echo -e "${BLUE}Using uv for dependency installation...${NC}"
        uv sync
    elif command -v pip >/dev/null 2>&1; then
        echo -e "${BLUE}Using pip for dependency installation...${NC}"
        pip install -r requirements.txt 2>/dev/null || echo -e "${YELLOW}Warning: Some ARC-AGI-2 dependencies may not have installed correctly${NC}"
    else
        echo -e "${RED}Error: Neither uv nor pip found. Please install dependencies manually.${NC}"
        cd ../..
        exit 1
    fi

    cd ../..
    echo -e "${GREEN}✓ ARC-AGI-2 dependencies installed${NC}"
fi

# Create default configuration files
echo -e "${BLUE}Creating default configuration files...${NC}"

# Quick test configuration
cat > benchmarks/configs/quick_test.yaml << 'EOF'
name: "quick_test"
description: "Quick algorithm comparison test"

benchmarks:
  - name: "simple_questions"
    questions:
      - "What is 2+2?"
      - "What is the capital of France?"

    models: ["gpt-4o-mini", "gpt-4o-mini"]
    algorithms: ["massgen", "treequest"]
    num_runs: 1
    max_duration: 30
EOF

# Algorithm comparison configuration
cat > benchmarks/configs/algorithm_comparison.yaml << 'EOF'
name: "algorithm_comparison"
description: "Compare MassGen and TreeQuest algorithms"

benchmarks:
  - name: "reasoning_tasks"
    questions:
      - "Explain quantum computing in simple terms"
      - "Design a sustainable transportation system"
      - "Compare the pros and cons of renewable energy"

    models: ["gpt-4o-mini", "claude-3-haiku", "gemini-flash"]
    algorithms: ["massgen", "treequest"]
    num_runs: 3
    max_duration: 120

  - name: "factual_questions"
    questions:
      - "Who invented the transistor?"
      - "When did World War I end?"
      - "What is the largest planet in our solar system?"

    models: ["gpt-4o-mini", "gpt-4o-mini"]
    algorithms: ["massgen", "treequest"]
    num_runs: 2
    max_duration: 30
EOF

# ARC-AGI-2 configuration (if available)
if [ -d "benchmarks/ab-mcts-arc2" ]; then
    cat > benchmarks/configs/arc_agi_2.yaml << 'EOF'
name: "arc_agi_2_evaluation"
description: "ARC-AGI-2 pattern recognition benchmarks"

# TreeQuest configuration (matches Sakana AI paper)
treequest_models:
  - "gpt-4o-mini"
  - "gemini-2.5-pro"
  - "openrouter/deepseek/deepseek-r1"

# MassGen configuration
massgen_models:
  - "gpt-4o-mini"
  - "gpt-4o-mini"
  - "gpt-4o-mini"

algorithms: ["massgen", "treequest"]
max_llm_calls: 250
num_runs: 3
task_ids: [0, 1, 2, 3, 4]  # First 5 tasks for testing
EOF
fi

echo -e "${GREEN}✓ Configuration files created${NC}"

# Test benchmark installation
echo -e "${BLUE}Testing benchmark installation...${NC}"

# Test basic benchmarks
python -c "
import sys
sys.path.append('.')
try:
    from benchmarks.run_benchmarks import BenchmarkRunner
    print('✓ Basic benchmarking available')
except Exception as e:
    print(f'✗ Basic benchmarking error: {e}')
    sys.exit(1)
"

# Test ARC-AGI-2 benchmarks if available
if [ -d "benchmarks/ab-mcts-arc2" ]; then
    python -c "
import sys
sys.path.append('.')
try:
    from benchmarks.sakana_benchmarks import SakanaBenchmarkRunner
    print('✓ ARC-AGI-2 benchmarking available')
except Exception as e:
    print(f'✗ ARC-AGI-2 benchmarking error: {e}')
    sys.exit(1)
"
fi

# Setup complete
echo -e "\n${GREEN}🎉 Benchmark setup complete!${NC}"

echo -e "\n${BLUE}Available benchmarks:${NC}"
echo -e "1. ${YELLOW}Basic Algorithm Comparison:${NC}"
echo -e "   python benchmarks/run_benchmarks.py --quick"
echo -e "   python benchmarks/run_benchmarks.py --config benchmarks/configs/algorithm_comparison.yaml"

if [ -d "benchmarks/ab-mcts-arc2" ]; then
    echo -e "\n2. ${YELLOW}ARC-AGI-2 Evaluation:${NC}"
    echo -e "   python benchmarks/sakana_benchmarks.py --quick"
    echo -e "   python benchmarks/sakana_benchmarks.py --config benchmarks/configs/arc_agi_2.yaml"
fi

echo -e "\n${BLUE}Configuration files:${NC}"
echo -e "- benchmarks/configs/quick_test.yaml"
echo -e "- benchmarks/configs/algorithm_comparison.yaml"
if [ -d "benchmarks/ab-mcts-arc2" ]; then
    echo -e "- benchmarks/configs/arc_agi_2.yaml"
fi

echo -e "\n${BLUE}Results will be saved to:${NC}"
echo -e "- benchmarks/results/general/"
echo -e "- benchmarks/results/sakana/"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Ensure your API keys are set (OPENROUTER_API_KEY recommended)"
echo -e "2. Run a quick test: ${BLUE}python benchmarks/run_benchmarks.py --quick${NC}"
echo -e "3. Check the results in benchmarks/results/"
echo -e "4. Read the full guide: ${BLUE}docs/benchmarking.md${NC}"

echo -e "\n${GREEN}Happy benchmarking! 🚀${NC}"
