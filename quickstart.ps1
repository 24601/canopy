# Canopy Quick Start Script for Windows
# This script helps you get Canopy up and running quickly on Windows

$ErrorActionPreference = "Stop"

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Banner
Write-ColorOutput Green @"
🌳 Canopy Quick Start Setup
==========================
"@

# Check Python version
Write-ColorOutput Blue "Checking Python version..."

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -eq 3 -and $minor -ge 10) {
            Write-ColorOutput Green "✓ $pythonVersion found"
        } else {
            Write-ColorOutput Red "Error: Python 3.10 or higher is required. Found: $pythonVersion"
            exit 1
        }
    }
} catch {
    Write-ColorOutput Red "Error: Python not found. Please install Python 3.10 or higher."
    Write-ColorOutput Blue "Download from: https://www.python.org/downloads/"
    exit 1
}

# Create virtual environment
Write-ColorOutput Blue "`nCreating virtual environment..."
python -m venv venv

# Activate virtual environment
Write-ColorOutput Blue "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Install Canopy
Write-ColorOutput Blue "`nInstalling Canopy..."
pip install --upgrade pip
pip install -e .

Write-ColorOutput Green "✓ Canopy installed successfully"

# Check for .env file
Write-ColorOutput Blue "`nChecking for API keys..."
if (-not (Test-Path .env)) {
    Write-ColorOutput Yellow "No .env file found. Let's create one!"
    Write-Host "`nYou'll need at least one API key to use Canopy."
    Write-Host "We recommend OpenRouter for access to all models with a single key."
    Write-ColorOutput Blue "`nGet your free API key at: https://openrouter.ai/"
    
    Write-ColorOutput Yellow "`nEnter your API key (or press Enter to skip):"
    
    # Create .env file
    New-Item -ItemType File -Path .env -Force | Out-Null
    
    # OpenRouter
    $openrouterKey = Read-Host "OpenRouter API Key"
    if ($openrouterKey) {
        Add-Content -Path .env -Value "OPENROUTER_API_KEY=$openrouterKey"
    }
    
    # Optional: Other providers
    Write-ColorOutput Yellow "`nOptional: Enter other API keys (press Enter to skip)"
    
    $openaiKey = Read-Host "OpenAI API Key"
    if ($openaiKey) {
        Add-Content -Path .env -Value "OPENAI_API_KEY=$openaiKey"
    }
    
    $anthropicKey = Read-Host "Anthropic API Key"
    if ($anthropicKey) {
        Add-Content -Path .env -Value "ANTHROPIC_API_KEY=$anthropicKey"
    }
    
    $geminiKey = Read-Host "Google AI API Key"
    if ($geminiKey) {
        Add-Content -Path .env -Value "GEMINI_API_KEY=$geminiKey"
    }
    
    Write-ColorOutput Green "✓ .env file created"
} else {
    Write-ColorOutput Green "✓ .env file found"
}

# Test installation
Write-ColorOutput Blue "`nTesting Canopy installation..."
try {
    python -m canopy --version | Out-Null
    Write-ColorOutput Green "✓ Canopy is ready to use!"
} catch {
    Write-ColorOutput Yellow "Warning: Could not verify Canopy installation"
}

# Show next steps
Write-ColorOutput Green "`n🎉 Setup Complete!"
Write-ColorOutput Blue "`nNext steps:"
Write-Host "1. Try a simple query:"
Write-ColorOutput Yellow '   python -m canopy "What is the meaning of life?" --models gpt-4o-mini claude-3-haiku'
Write-Host "`n2. Start the API server:"
Write-ColorOutput Yellow "   python -m canopy --serve"
Write-Host "`n3. Use interactive mode:"
Write-ColorOutput Yellow "   python -m canopy --models gpt-4o-mini claude-3-haiku --interactive"
Write-Host "`n4. Check out the quickstart guide:"
Write-ColorOutput Yellow "   docs\quickstart\README.md"

# Activation reminder
Write-ColorOutput Yellow "`nRemember to activate the virtual environment in new terminals:"
Write-ColorOutput Blue "   .\venv\Scripts\Activate.ps1"

Write-ColorOutput Green "`nHappy multi-agent consensus building! 🌳"