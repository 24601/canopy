#!/bin/bash
# Canopy Quick Start Script
# This script helps you get Canopy up and running quickly

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${GREEN}"
echo "🌳 Canopy Quick Start Setup"
echo "=========================="
echo -e "${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
if command_exists python3; then
    PYTHON_CMD=python3
elif command_exists python; then
    PYTHON_CMD=python
else
    echo -e "${RED}Error: Python not found. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

# Check Python version is 3.10+
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo -e "\n${BLUE}Creating virtual environment...${NC}"
$PYTHON_CMD -m venv venv

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix-like
    source venv/bin/activate
fi

# Install Canopy
echo -e "\n${BLUE}Installing Canopy...${NC}"
pip install --upgrade pip
pip install -e .

echo -e "${GREEN}✓ Canopy installed successfully${NC}"

# Check for .env file
echo -e "\n${BLUE}Checking for API keys...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Let's create one!${NC}"
    echo -e "\nYou'll need at least one API key to use Canopy."
    echo -e "We recommend OpenRouter for access to all models with a single key."
    echo -e "\nGet your free API key at: ${BLUE}https://openrouter.ai/${NC}"
    
    echo -e "\n${YELLOW}Enter your API key (or press Enter to skip):${NC}"
    
    # Create .env file
    touch .env
    
    # OpenRouter
    read -p "OpenRouter API Key: " OPENROUTER_KEY
    if [ ! -z "$OPENROUTER_KEY" ]; then
        echo "OPENROUTER_API_KEY=$OPENROUTER_KEY" >> .env
    fi
    
    # Optional: Other providers
    echo -e "\n${YELLOW}Optional: Enter other API keys (press Enter to skip)${NC}"
    
    read -p "OpenAI API Key: " OPENAI_KEY
    if [ ! -z "$OPENAI_KEY" ]; then
        echo "OPENAI_API_KEY=$OPENAI_KEY" >> .env
    fi
    
    read -p "Anthropic API Key: " ANTHROPIC_KEY
    if [ ! -z "$ANTHROPIC_KEY" ]; then
        echo "ANTHROPIC_API_KEY=$ANTHROPIC_KEY" >> .env
    fi
    
    read -p "Google AI API Key: " GEMINI_KEY
    if [ ! -z "$GEMINI_KEY" ]; then
        echo "GEMINI_API_KEY=$GEMINI_KEY" >> .env
    fi
    
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi

# Test installation
echo -e "\n${BLUE}Testing Canopy installation...${NC}"
if $PYTHON_CMD -m canopy --version >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Canopy is ready to use!${NC}"
else
    echo -e "${YELLOW}Warning: Could not verify Canopy installation${NC}"
fi

# Show next steps
echo -e "\n${GREEN}🎉 Setup Complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Try a simple query:"
echo -e "   ${YELLOW}python -m canopy \"What is the meaning of life?\" --models gpt-4o-mini claude-3-haiku${NC}"
echo -e "\n2. Start the API server:"
echo -e "   ${YELLOW}python -m canopy --serve${NC}"
echo -e "\n3. Use interactive mode:"
echo -e "   ${YELLOW}python -m canopy --models gpt-4o-mini claude-3-haiku --interactive${NC}"
echo -e "\n4. Check out the quickstart guide:"
echo -e "   ${YELLOW}docs/quickstart/README.md${NC}"

# Activation reminder
echo -e "\n${YELLOW}Remember to activate the virtual environment in new terminals:${NC}"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo -e "   ${BLUE}venv\\Scripts\\activate${NC}"
else
    echo -e "   ${BLUE}source venv/bin/activate${NC}"
fi

echo -e "\n${GREEN}Happy multi-agent consensus building! 🌳${NC}"