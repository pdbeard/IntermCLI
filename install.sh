#!/bin/bash
# IntermCLI Installation Script
# Interactive terminal utilities for developers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    INSTALL_DIR="$HOME/.local/bin"
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    INSTALL_DIR="$HOME/.local/bin"
    PLATFORM="macOS"
else
    echo -e "${RED}❌ Unsupported platform: $OSTYPE${NC}"
    exit 1
fi

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🔧 Installing IntermCLI on $PLATFORM...${NC}"
echo ""

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Install individual tools
echo -e "${BLUE}📦 Installing tools...${NC}"

# Create wrapper scripts for each tool
if [ -f "$SCRIPT_ROOT/tools/scan-ports/scan-ports.py" ]; then
    cat > "$INSTALL_DIR/scan-ports" << 'EOF'
#!/bin/bash
# IntermCLI scan-ports wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_PATH="$(dirname "$SCRIPT_DIR")/dev/scripts/IntermCLI/tools/scan-ports/scan-ports.py"
if [ -f "$TOOL_PATH" ]; then
    python3 "$TOOL_PATH" "$@"
else
    python3 -c "
import sys, os
script_dir = os.path.dirname(os.path.realpath('$0'))
possible_paths = [
    os.path.expanduser('~/dev/scripts/IntermCLI/tools/scan-ports/scan-ports.py'),
    os.path.join(script_dir, '../tools/scan-ports/scan-ports.py'),
    os.path.join(script_dir, '../../IntermCLI/tools/scan-ports/scan-ports.py')
]
for path in possible_paths:
    if os.path.exists(path):
        import subprocess
        sys.exit(subprocess.call([sys.executable, path] + sys.argv[1:]))
print('❌ scan-ports tool not found')
sys.exit(1)
" "$@"
fi
EOF
    chmod +x "$INSTALL_DIR/scan-ports"
    echo -e "${GREEN}  ✅ scan-ports${NC}"
fi

if [ -f "$SCRIPT_ROOT/tools/find-projects/find-projects.py" ]; then
    cat > "$INSTALL_DIR/find-projects" << 'EOF'
#!/bin/bash
# IntermCLI find-projects wrapper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_PATH="$(dirname "$SCRIPT_DIR")/dev/scripts/IntermCLI/tools/find-projects/find-projects.py"
if [ -f "$TOOL_PATH" ]; then
    python3 "$TOOL_PATH" "$@"
else
    python3 -c "
import sys, os
script_dir = os.path.dirname(os.path.realpath('$0'))
possible_paths = [
    os.path.expanduser('~/dev/scripts/IntermCLI/tools/find-projects/find-projects.py'),
    os.path.join(script_dir, '../tools/find-projects/find-projects.py'),
    os.path.join(script_dir, '../../IntermCLI/tools/find-projects/find-projects.py')
]
for path in possible_paths:
    if os.path.exists(path):
        import subprocess
        sys.exit(subprocess.call([sys.executable, path] + sys.argv[1:]))
print('❌ find-projects tool not found')
sys.exit(1)
" "$@"
fi
EOF
    chmod +x "$INSTALL_DIR/find-projects"
    echo -e "${GREEN}  ✅ find-projects${NC}"
fi

# Check for legacy tools and migrate
if [ -f "$SCRIPT_ROOT/lib/port-check.py" ]; then
    echo -e "${YELLOW}  📋 Found legacy port-check.py, consider migrating to scan-ports${NC}"
fi

if [ -f "$SCRIPT_ROOT/lib/project-finder.py" ]; then
    echo -e "${YELLOW}  📋 Found legacy project-finder.py, consider migrating to find-projects${NC}"
fi

echo ""

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${GREEN}  ✅ Python $PYTHON_VERSION found${NC}"
    
    # Check if version is 3.8+
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        echo -e "${GREEN}  ✅ Python version compatible${NC}"
    else
        echo -e "${YELLOW}  ⚠️  Python 3.8+ recommended (current: $PYTHON_VERSION)${NC}"
    fi
else
    echo -e "${RED}  ❌ Python 3 not found${NC}"
    echo -e "${YELLOW}     Please install Python 3.8+ to use IntermCLI${NC}"
fi

echo ""

# Check PATH
echo -e "${BLUE}🛤️  Checking PATH configuration...${NC}"
if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    echo -e "${GREEN}  ✅ $INSTALL_DIR is in PATH${NC}"
else
    echo -e "${YELLOW}  ⚠️  $INSTALL_DIR is not in PATH${NC}"
    echo -e "${YELLOW}     Add to your shell profile (~/.bashrc, ~/.zshrc, etc.):${NC}"
    echo -e "${BLUE}     export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
fi

echo ""

# Optional dependencies check
echo -e "${BLUE}📦 Optional dependencies status:${NC}"
python3 -c "
import sys
try:
    import requests
    print('  ✅ requests (enhanced HTTP scanning)')
except ImportError:
    print('  ⚪ requests (enhanced HTTP scanning)')

try:
    import rich
    print('  ✅ rich (enhanced terminal output)')
except ImportError:
    print('  ⚪ rich (enhanced terminal output)')

try:
    import click
    print('  ✅ click (enhanced CLI)')
except ImportError:
    print('  ⚪ click (enhanced CLI)')
"

echo ""
echo -e "${GREEN}✅ IntermCLI installation complete!${NC}"
echo ""
echo -e "${BLUE}🚀 Quick start:${NC}"
echo -e "  ${GREEN}scan-ports localhost${NC}     # Scan local ports"
echo -e "  ${GREEN}find-projects${NC}            # Find development projects"
echo ""
echo -e "${BLUE}📚 For enhanced features:${NC}"
echo -e "  ${GREEN}pip3 install -r requirements.txt${NC}"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo -e "  ${GREEN}docs/ARCHITECTURE.md${NC}     # Project structure"
echo -e "  ${GREEN}docs/DESIGN.md${NC}           # Design philosophy"