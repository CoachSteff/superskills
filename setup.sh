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
echo "  1) pipx - Global access (recommended for most users)"
echo "  2) Virtual environment (for developers)"
echo "  3) User install (pip install --user)"
echo ""
read -p "Enter choice [1-3]: " INSTALL_METHOD
# Trim whitespace
INSTALL_METHOD=$(echo "$INSTALL_METHOD" | tr -d '[:space:]')

case $INSTALL_METHOD in
    1)
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
            echo ""
            echo "⚠ Important: You may need to restart your terminal"
            echo "  for the PATH changes to take effect."
            echo ""
        fi
        
        # Install with pipx
        echo "Installing SuperSkills globally..."
        pipx install -e "$PROJECT_ROOT"
        echo "✓ SuperSkills installed globally"
        
        INSTALLED_PATH=$(which superskills 2>/dev/null || echo "superskills")
        ACTIVATION_CMD=""
        IS_GLOBAL=true
        ;;
        
    2)
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
        IS_GLOBAL=false
        ;;
        
    3)
        echo ""
        echo "Installing with pip --user..."
        
        # Install package
        $PYTHON_CMD -m pip install --user -e "$PROJECT_ROOT"
        echo "✓ SuperSkills installed"
        
        INSTALLED_PATH="$HOME/.local/bin/superskills"
        ACTIVATION_CMD=""
        IS_GLOBAL=true
        
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

# Verify installation
echo "=========================================="
echo "Verifying Installation"
echo "=========================================="
echo ""

if [ "$IS_GLOBAL" = true ]; then
    # Test from different directory
    ORIGINAL_DIR=$(pwd)
    cd /tmp
    
    if command -v superskills &> /dev/null; then
        echo "✓ 'superskills' command is globally accessible"
        superskills --version 2>/dev/null || echo "  (version info unavailable)"
    else
        echo "⚠ Warning: 'superskills' command not found in PATH"
        echo "  You may need to restart your terminal or run:"
        echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    cd "$ORIGINAL_DIR"
else
    echo "✓ SuperSkills installed in virtual environment"
    echo "  Activate with: $ACTIVATION_CMD"
fi

echo ""

# Initialize CLI
if [ "$INSTALL_METHOD" = "2" ]; then
    echo "Initializing SuperSkills CLI..."
    "$PROJECT_ROOT/.venv/bin/superskills" init || true
else
    echo "Initializing SuperSkills CLI..."
    superskills init 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""

if [ "$INSTALL_METHOD" = "2" ]; then
    echo "1. Activate the virtual environment:"
    echo "   $ACTIVATION_CMD"
    echo ""
    echo "2. Set your API keys in environment or .env file:"
else
    echo "1. Set your API keys in environment or .env file:"
fi
echo "   export ANTHROPIC_API_KEY=your_key_here"
echo "   export ELEVENLABS_API_KEY=your_key_here"
echo ""

if [ "$INSTALL_METHOD" = "2" ]; then
    echo "3. Try the CLI:"
else
    echo "2. Try the CLI:"
fi
echo "   superskills list"
echo "   superskills call researcher \"AI automation trends\""
echo "   superskills run content-creation --topic \"Your topic\""
echo ""

if [ "$INSTALL_METHOD" = "2" ]; then
    echo "4. Create personalized profiles for skills:"
else
    echo "3. Create personalized profiles for skills:"
fi
echo "   cp superskills/copywriter/PROFILE.md.template superskills/copywriter/PROFILE.md"
echo "   # Edit PROFILE.md with your tone-of-voice"
echo ""

echo "For more information, see:"
echo "  - QUICKSTART.md - Quick command reference"
echo "  - README.md - Full documentation"
echo ""

if [ "$INSTALL_METHOD" = "2" ]; then
    echo "=========================================="
    echo "Virtual Environment Quick Reference"
    echo "=========================================="
    echo ""
    echo "Activate:   $ACTIVATION_CMD"
    echo "Deactivate: deactivate"
    echo ""
fi

echo "Setup complete! 🎉"
