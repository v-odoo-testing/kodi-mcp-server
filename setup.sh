#!/bin/bash
# Setup script for Kodi MCP Server

set -e

echo "🚀 Setting up Kodi MCP Server..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]]; then
    echo "❌ Python 3.8+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your Kodi connection:"
echo "   export KODI_HOST='192.168.1.71'"
echo "   export KODI_USERNAME='kodi'"
echo "   export KODI_PASSWORD='kodi'"
echo ""
echo "2. Test the connection:"
echo "   source venv/bin/activate"
echo "   python test_connection.py"
echo ""
echo "3. Add to Claude Desktop config:"
echo "   See claude-desktop-config.json for configuration"
echo ""
echo "🎉 Ready to use Kodi MCP Server!"
