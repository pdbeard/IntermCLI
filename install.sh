#!/bin/bash
# filepath: /Users/patrick/development/linux_scripts/install.sh
# Install linux_scripts to user's local bin directory
# Works on both Linux and macOS

set -e

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    INSTALL_DIR="$HOME/.local/bin"
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    INSTALL_DIR="$HOME/.local/bin"
    PLATFORM="macOS"
else
    echo "❌ Unsupported platform: $OSTYPE"
    exit 1
fi

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Installing linux_scripts on $PLATFORM..."

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Copy executable scripts
cp "$SCRIPT_ROOT/bin/"* "$INSTALL_DIR/"

# Make sure they're executable
chmod +x "$INSTALL_DIR/"*

echo "✅ Scripts installed to $INSTALL_DIR"
echo ""
echo "Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
echo "export PATH=\"\$HOME/.local/bin:\$PATH\""