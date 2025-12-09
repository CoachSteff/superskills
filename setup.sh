#!/usr/bin/env bash
#
# SuperSkills Setup Script
# Automates the installation and configuration of the SuperSkills CLI
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "SuperSkills Setup"
echo "=========================================="
echo ""

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "Error: Python not found. Please install Python 3.9 or higher."
    exit 1
fi

echo "✓ Found Python: $PYTHON_CMD"
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
echo "  Version: $PYTHON_VERSION"
echo ""

# Check Python version
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "Error: Python 3.9 or higher required. Found: $PYTHON_VERSION"
    exit 1
fi

# Detect installation method
echo "Select installation method:"
echo "  1) Virtual environment (recommended)"
echo "  2) pipx (for global access)"
echo "  3) User install (pip install --user)"
echo ""
read -p "Enter choice [1-3]: " INSTALL_METHOD

case $INSTALL_METHOD in
    1)
        echo ""
        echo "Installing with virtual environment..."
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "$PROJECT_ROOT/.venv" ]; then
            echo "Creating virtual environment..."
            $PYTHON_CMD -m venv "$PROJECT_ROOT/.venv"
            echo "✓ Virtual environment created at .venv/"
        else
            echo "✓ Virtual environment already exists at .venv/"
        fi
        
        # Activate virtual environment
        source "$PROJECT_ROOT/.venv/bin/activate"
        echo "✓ Virtual environment activated"
        
        # Upgrade pip
        echo "Upgrading pip..."
        pip install --upgrade pip --quiet
        
        # Install package
        echo "Installing superskills..."
        pip install -e "$PROJECT_ROOT" --quiet
        echo "✓ SuperSkills installed"
        
        INSTALLED_PATH="$PROJECT_ROOT/.venv/bin/superskills"
        ACTIVATION_CMD="source $PROJECT_ROOT/.venv/bin/activate"
        ;;
        
    2)
        echo ""
        echo "Installing with pipx..."
        
        # Check if pipx is installed
        if ! command -v pipx &> /dev/null; then
            echo "pipx not found. Installing..."
            
            if command -v brew &> /dev/null; then
                brew install pipx
            else
                $PYTHON_CMD -m pip install --user pipx
                $PYTHON_CMD -m pipx ensurepath
            fi
            
            echo "✓ pipx installed"
        fi
        
        # Install with pipx
        pipx install -e "$PROJECT_ROOT"
        echo "✓ SuperSkills installed globally"
        
        INSTALLED_PATH=$(which superskills)
        ACTIVATION_CMD=""
        ;;
        
    3)
        echo ""
        echo "Installing with pip --user..."
        
        # Install package
        $PYTHON_CMD -m pip install --user -e "$PROJECT_ROOT"
        echo "✓ SuperSkills installed"
        
        INSTALLED_PATH="$HOME/.local/bin/superskills"
        ACTIVATION_CMD=""
        
        # Check if .local/bin is in PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo ""
            echo "⚠ Warning: $HOME/.local/bin is not in your PATH"
            echo "  Add this to your ~/.zshrc or ~/.bashrc:"
            echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
        fi
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""

# Initialize CLI
if [ "$INSTALL_METHOD" = "1" ]; then
    echo "Initializing SuperSkills CLI..."
    "$PROJECT_ROOT/.venv/bin/superskills" init || true
else
    echo "Initializing SuperSkills CLI..."
    superskills init || true
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""

if [ "$INSTALL_METHOD" = "1" ]; then
    echo "1. Activate the virtual environment:"
    echo "   $ACTIVATION_CMD"
    echo ""
fi

echo "2. Set your API keys in environment or .env file:"
echo "   export ANTHROPIC_API_KEY=your_key_here"
echo "   export ELEVENLABS_API_KEY=your_key_here"
echo ""

echo "3. Try the CLI:"
echo "   superskills list"
echo "   superskills call researcher \"AI automation trends\""
echo "   superskills run content-creation --topic \"Your topic\""
echo ""

echo "4. Create personalized profiles for skills:"
echo "   cp superskills/copywriter/PROFILE.md.template superskills/copywriter/PROFILE.md"
echo "   # Edit PROFILE.md with your tone-of-voice"
echo ""

echo "For more information, see:"
echo "  - CLI_SETUP.md - Installation and usage guide"
echo "  - README.md - Full documentation"
echo ""

if [ "$INSTALL_METHOD" = "1" ]; then
    echo "=========================================="
    echo "Virtual Environment Quick Reference"
    echo "=========================================="
    echo ""
    echo "Activate:   $ACTIVATION_CMD"
    echo "Deactivate: deactivate"
    echo ""
fi

echo "Setup complete! 🎉"
