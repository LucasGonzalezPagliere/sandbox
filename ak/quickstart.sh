#!/bin/bash

echo "🚀 Smart Reading List - Quick Start Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    echo "  Try: pip install -r requirements.txt"
    exit 1
fi
echo ""

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating configuration file..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env and add your API keys:"
    echo "   1. Get Anthropic API key from: https://console.anthropic.com/"
    echo "   2. Set up Gmail app password (see SETUP.md)"
    echo ""
    echo "Edit .env now? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "✓ .env file already exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/audio
mkdir -p templates
echo "✓ Directories created"
echo ""

# Initialize database
echo "💾 Initializing database..."
python3 -c "from database import Database; Database()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Database initialized"
else
    echo "ℹ Database will be created on first run"
fi
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure you've configured .env with your API keys"
echo "  2. Run: python3 app.py"
echo "  3. Open: http://localhost:5000"
echo ""
echo "For detailed setup instructions, see SETUP.md"
echo ""
