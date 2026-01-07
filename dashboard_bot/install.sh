#!/usr/bin/env bash
set -e

# Dashboard Bot Installer for Linux/macOS
# This script sets up the development environment automatically

echo "🤖 Dashboard Bot - Installer"
echo "============================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $PYTHON_VERSION detected. Python 3.8 or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed."
    echo "Please install Git from https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git $(git --version | cut -d' ' -f3) detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Dependencies installed"

# Initialize configuration
echo "🔧 Setting up configuration..."

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "⚠️  IMPORTANT: Please configure the following in .env:"
    echo "   - GOOGLE_API_KEY (for Gemini)"
    echo "   - JIRA_URL, JIRA_EMAIL, JIRA_TOKEN"
    echo "   - MS_CLIENT_ID, MS_AUTHORITY (for Outlook)"
    echo "   - OBSIDIAN_VAULT_PATH"
else
    echo "⚠️  .env file already exists. Skipping creation."
fi

# Create artifacts directory if it doesn't exist
if [ ! -d "artifacts" ]; then
    mkdir -p artifacts
    echo "✅ Created artifacts directory"
fi

# Create openspec directory if it doesn't exist
if [ ! -d "openspec" ]; then
    mkdir -p openspec
    echo "✅ Created openspec directory"
fi

# Create tests directory if it doesn't exist
if [ ! -d "tests" ]; then
    mkdir -p tests
    echo "✅ Created tests directory"
fi

echo ""
echo "============================="
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Configure your API keys in .env file:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the agent:"
echo "   python agent.py \"Create today's daily note with my tasks and emails\""
echo ""
echo "📚 See mission.md for full objective description"
echo "============================="
