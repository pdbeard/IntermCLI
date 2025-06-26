#!/bin/bash
set -e

# Colors FIRST (before any usage)
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# IntermCLI Installation Script
# Interactive terminal utilities for developers

# DEFINE FUNCTIONS FIRST
validate_environment() {
    # Check if running as root (usually not desired for user tools)
    if [ "$EUID" -eq 0 ] && [ "$INSTALL_SCOPE" = "user" ]; then
        echo -e "${YELLOW}⚠️  Running as root but installing to user directory${NC}"
        if ! ask_yes_no "Continue anyway?" "n"; then
            exit 1
        fi
    fi
    
    # Validate write permissions
    if [ "$INSTALL_SCOPE" = "user" ] && [ ! -w "$(dirname "$USER_INSTALL_DIR")" ]; then
        echo -e "${RED}❌ Cannot write to $USER_INSTALL_DIR${NC}"
        exit 1
    fi
}

detect_shell_profile() {
    if [ -n "$ZSH_VERSION" ] || [[ "$SHELL" == */zsh ]]; then
        echo "$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [[ "$SHELL" == */bash ]]; then
        if [[ "$OSTYPE" == "darwin"* ]] && [ -f "$HOME/.bash_profile" ]; then
            echo "$HOME/.bash_profile"
        else
            echo "$HOME/.bashrc"
        fi
    else
        echo ""
    fi
}

verify_installation() {
    echo -e "${BLUE}🔍 Verifying installation...${NC}"
    
    for tool in "scan-ports" "find-projects"; do
        if [ -f "$INSTALL_DIR/$tool" ] && [ -x "$INSTALL_DIR/$tool" ]; then
            echo -e "${GREEN}  ✅ $tool installed and executable${NC}"
        else
            echo -e "${RED}  ❌ $tool installation failed${NC}"
            return 1
        fi
    done
    
    # Test basic functionality
    if command -v python3 >/dev/null && python3 -c "import sys; print('Python', sys.version)" >/dev/null 2>&1; then
        echo -e "${GREEN}  ✅ Python environment working${NC}"
    fi
}

# Interactive prompts
ask_yes_no() {
    local prompt="$1"
    local default="$2"
    local response
    
    if [ "$default" = "y" ]; then
        prompt="$prompt [Y/n]: "
    else
        prompt="$prompt [y/N]: "
    fi
    
    while true; do
        read -p "$prompt" response
        # Convert to lowercase using tr instead of ${response,,}
        response=$(echo "$response" | tr '[:upper:]' '[:lower:]')
        case $response in
            y|yes) return 0 ;;
            n|no) return 1 ;;
            "") 
                if [ "$default" = "y" ]; then
                    return 0
                else
                    return 1
                fi
                ;;
            *) echo "Please answer yes or no." ;;
        esac
    done
}

# Handle command-line arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "IntermCLI Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --version, -v  Show version information"
    echo "  --uninstall    Remove IntermCLI"
    echo "  --dry-run      Show what would be installed without installing"
    exit 0
fi

if [ "$1" = "--version" ] || [ "$1" = "-v" ]; then
    echo "IntermCLI Installation Script v1.0.0"
    exit 0
fi

if [ "$1" = "--uninstall" ]; then
    echo -e "${BLUE}🗑️  Uninstalling IntermCLI...${NC}"
    
    if ask_yes_no "Remove installed tools?" "y"; then
        rm -f "$HOME/.local/bin/scan-ports" "$HOME/.local/bin/find-projects"
        echo -e "${GREEN}  ✅ Tools removed${NC}"
    fi
    
    if ask_yes_no "Remove configuration?" "n"; then
        rm -rf "$HOME/.config/intermcli"
        echo -e "${GREEN}  ✅ Configuration removed${NC}"
    fi
    
    echo -e "${GREEN}✅ Uninstall complete${NC}"
    exit 0
fi

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${BLUE}🔍 Dry run mode - showing what would be installed${NC}"
fi

# Detect platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    USER_INSTALL_DIR="$HOME/.local/bin"
    GLOBAL_INSTALL_DIR="/usr/local/bin"
    PLATFORM="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    USER_INSTALL_DIR="$HOME/.local/bin"
    GLOBAL_INSTALL_DIR="/usr/local/bin"
    PLATFORM="macOS"
else
    echo -e "${RED}❌ Unsupported platform: $OSTYPE${NC}"
    exit 1
fi

SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLED_FILES=()
INSTALLED_DIRS=()

# Add logging capability
LOG_FILE="$HOME/.intermcli-install.log"

log() {
    echo "$(date): $1" >> "$LOG_FILE"
}

cleanup_on_failure() {
    echo -e "${RED}Installation failed, cleaning up...${NC}"
    for file in "${INSTALLED_FILES[@]}"; do
        rm -f "$file" 2>/dev/null && echo -e "${YELLOW}  Removed: $file${NC}"
    done
    for dir in "${INSTALLED_DIRS[@]}"; do
        rmdir "$dir" 2>/dev/null && echo -e "${YELLOW}  Removed: $dir${NC}"
    done
}

trap cleanup_on_failure ERR
# Global interrupt and error handling
cleanup_on_exit() {
    local exit_code=$?
    if [ $exit_code -eq 130 ]; then
        echo -e "\n${YELLOW}Installation cancelled by user (Ctrl+C)${NC}"
    elif [ $exit_code -ne 0 ]; then
        echo -e "\n${RED}Installation failed, cleaning up...${NC}"
        for file in "${INSTALLED_FILES[@]}"; do
            rm -f "$file" 2>/dev/null && echo -e "${YELLOW}  Removed: $file${NC}"
        done
        for dir in "${INSTALLED_DIRS[@]}"; do
            rmdir "$dir" 2>/dev/null && echo -e "${YELLOW}  Removed: $dir${NC}"
        done
    fi
    exit $exit_code
}

# Handle both errors and interrupts
trap cleanup_on_exit ERR INT TERM

# Welcome message
echo -e "${BLUE}🔧 IntermCLI Interactive Installation${NC}"
echo -e "${BLUE}   Installing on $PLATFORM${NC}"
echo ""

log "Starting installation on $PLATFORM"

# Check Python version and TOML support
echo -e "${BLUE}🐍 Checking Python compatibility...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo -e "${YELLOW}   Please install Python 3.11+ to use IntermCLI${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

echo -e "${GREEN}  ✅ Python $PYTHON_VERSION found${NC}"

# Check TOML support
TOML_SUPPORT=$(python3 -c "
try:
    import tomllib
    print('builtin')
except ImportError:
    try:
        import tomli
        print('tomli')
    except ImportError:
        print('none')
")

if [ "$TOML_SUPPORT" = "builtin" ]; then
    echo -e "${GREEN}  ✅ Built-in TOML support (Python 3.11+)${NC}"
    NEEDS_TOMLI=false
elif [ "$TOML_SUPPORT" = "tomli" ]; then
    echo -e "${GREEN}  ✅ TOML support via tomli package${NC}"
    NEEDS_TOMLI=false
else
    echo -e "${YELLOW}  ⚠️  No TOML support found${NC}"
    if [ $PYTHON_MAJOR -eq 3 ] && [ $PYTHON_MINOR -ge 8 ]; then
        echo -e "${YELLOW}     Python $PYTHON_VERSION can use tomli package${NC}"
        NEEDS_TOMLI=true
    else
        echo -e "${RED}❌ Python 3.8+ required for IntermCLI${NC}"
        exit 1
    fi
fi

echo ""

# Check dependencies using requirements.txt
echo -e "${BLUE}📦 Checking dependencies...${NC}"
MISSING_DEPS=()
OPTIONAL_MISSING=()

if [ "$NEEDS_TOMLI" = true ]; then
    MISSING_DEPS+=("tomli")
fi

# Read and check requirements.txt
if [ -f "$SCRIPT_ROOT/requirements.txt" ]; then
    echo -e "${BLUE}  Reading requirements.txt...${NC}"
    
    # Use mktemp for secure temp files
    TEMP_FILE=$(mktemp -t intermcli.XXXXXX)
    trap 'rm -f "$TEMP_FILE"' EXIT INT TERM
    
    # Parse requirements.txt and check each package
    python3 -c "
import sys
import re

# Read requirements.txt
with open('$SCRIPT_ROOT/requirements.txt', 'r') as f:
    lines = f.readlines()

missing_deps = []
available_deps = []

for line in lines:
    line = line.strip()
    # Skip comments and empty lines
    if not line or line.startswith('#'):
        continue
    
    # Handle conditional dependencies (e.g., tomli for Python < 3.11)
    if ';' in line:
        pkg_part, condition_part = line.split(';', 1)
        pkg_part = pkg_part.strip()
        condition_part = condition_part.strip()
        
        # Check if condition applies to current Python version
        if 'python_version' in condition_part:
            # Simple evaluation for common cases
            if 'python_version < \"3.11\"' in condition_part:
                if sys.version_info >= (3, 11):
                    # Skip this package for Python 3.11+
                    continue
            elif 'python_version >= \"3.11\"' in condition_part:
                if sys.version_info < (3, 11):
                    # Skip this package for Python < 3.11
                    continue
    else:
        pkg_part = line
    
    # Extract package name (before >= or other version specifiers)
    pkg_name = re.split(r'[><=!]', pkg_part)[0].strip()
    
    try:
        __import__(pkg_name.replace('-', '_'))  # Handle package name differences
        available_deps.append(pkg_name)
    except ImportError:
        missing_deps.append(pkg_name)

# Display results
for pkg in available_deps:
    print(f'  ✅ {pkg}')

for pkg in missing_deps:
    print(f'  ⚪ {pkg} - optional')

# Write missing deps to temp file
with open('$TEMP_FILE', 'w') as f:
    f.write('\n'.join(missing_deps))
"
    
    # Read the temp file
    OPTIONAL_MISSING=($(cat "$TEMP_FILE" 2>/dev/null || true))
    
    # Clean up temp file
    rm -f "$TEMP_FILE"
else
    echo -e "${YELLOW}  ⚠️  requirements.txt not found${NC}"
fi

# Dependency installation prompt
if [ ${#MISSING_DEPS[@]} -gt 0 ] || [ ${#OPTIONAL_MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}📋 Dependency Summary:${NC}"
    
    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo -e "${RED}  Required:${NC}"
        for dep in "${MISSING_DEPS[@]}"; do
            echo -e "    • $dep"
        done
    fi
    
    if [ ${#OPTIONAL_MISSING[@]} -gt 0 ]; then
        echo -e "${BLUE}  Optional (from requirements.txt):${NC}"
        for dep in "${OPTIONAL_MISSING[@]}"; do
            echo -e "    • $dep"
        done
    fi
    
    echo ""
    echo -e "${BLUE}Dependencies will be installed to user environment (~/.local/)${NC}"
    
    if ask_yes_no "Install dependencies automatically?" "y"; then
        INSTALL_DEPS=true
        
        if [ ${#OPTIONAL_MISSING[@]} -gt 0 ]; then
            if ask_yes_no "Include optional dependencies for enhanced features?" "y"; then
                INSTALL_OPTIONAL=true
            else
                INSTALL_OPTIONAL=false
            fi
        fi
    else
        INSTALL_DEPS=false
        echo -e "${YELLOW}  ⚠️  You can install dependencies manually later:${NC}"
        echo -e "${BLUE}     pip3 install --user -r $SCRIPT_ROOT/requirements.txt${NC}"
    fi
fi

# Installation scope
echo ""
echo -e "${BLUE}🎯 Installation Scope:${NC}"
echo -e "  ${GREEN}User installation:${NC} $USER_INSTALL_DIR (recommended for terminal tools)"
echo -e "  ${YELLOW}Global installation:${NC} $GLOBAL_INSTALL_DIR (system-wide, requires sudo)"
echo ""
echo -e "${BLUE}ℹ️  User installation is recommended for terminal utilities${NC}"
echo -e "   Tools will be available in your terminal after adding to PATH${NC}"

if ask_yes_no "Use user installation (recommended)?" "y"; then
    INSTALL_DIR="$USER_INSTALL_DIR"
    INSTALL_SCOPE="user"
else
    INSTALL_DIR="$GLOBAL_INSTALL_DIR"
    INSTALL_SCOPE="global"
    echo -e "${YELLOW}  ⚠️  Global installation requires administrator privileges${NC}"
fi

# VALIDATE ENVIRONMENT AFTER DETERMINING SCOPE
validate_environment

# Config directory setup
echo ""
echo -e "${BLUE}⚙️  Configuration Setup:${NC}"
CONFIG_DIR="$HOME/.config/intermcli"

if [ -d "$CONFIG_DIR" ]; then
    echo -e "${GREEN}  ✅ Config directory exists: $CONFIG_DIR${NC}"
else
    echo -e "${BLUE}  📁 Creating config directory: $CONFIG_DIR${NC}"
    mkdir -p "$CONFIG_DIR"
fi

if [ -f "$CONFIG_DIR/config.toml" ]; then
    echo -e "${YELLOW}  ⚠️  Existing config found${NC}"
    if ask_yes_no "Backup and update config file?" "y"; then
        cp "$CONFIG_DIR/config.toml" "$CONFIG_DIR/config.toml.backup"
        cp "$SCRIPT_ROOT/tools/find-projects/config/defaults.toml" "$CONFIG_DIR/config.toml"
        echo -e "${GREEN}  ✅ Config updated (backup saved)${NC}"
    fi
else
    cp "$SCRIPT_ROOT/tools/find-projects/config/defaults.toml" "$CONFIG_DIR/config.toml"
    echo -e "${GREEN}  ✅ Default config created${NC}"
fi

# Installation summary
echo ""
echo -e "${BLUE}📋 Installation Summary:${NC}"
echo -e "  Platform: $PLATFORM"
echo -e "  Python: $PYTHON_VERSION"
echo -e "  Install to: $INSTALL_DIR"
echo -e "  Config: $CONFIG_DIR"
if [ "$INSTALL_DEPS" = true ]; then
    echo -e "  Dependencies: Will install"
else
    echo -e "  Dependencies: Skip"
fi

echo ""
if ! ask_yes_no "Proceed with installation?" "y"; then
    echo -e "${YELLOW}Installation cancelled${NC}"
    exit 0
fi

# Start installation
echo ""
echo -e "${BLUE}🚀 Starting installation...${NC}"

# Install dependencies
if [ "$INSTALL_DEPS" = true ]; then
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    
    # Build list of packages to install
    DEPS_TO_INSTALL=("${MISSING_DEPS[@]}")
    if [ "$INSTALL_OPTIONAL" = true ]; then
        DEPS_TO_INSTALL+=("${OPTIONAL_MISSING[@]}")
    fi
    
    if [ ${#DEPS_TO_INSTALL[@]} -gt 0 ]; then
        echo -e "${BLUE}  Installing: ${DEPS_TO_INSTALL[*]}${NC}"
        
        if [ "$DRY_RUN" = false ]; then
            if pip3 install --user "${DEPS_TO_INSTALL[@]}"; then
                echo -e "${GREEN}  ✅ Dependencies installed${NC}"
            else
                echo -e "${YELLOW}  ⚠️  Failed to install some packages${NC}"
                echo -e "${YELLOW}     Manual install: pip3 install --user ${DEPS_TO_INSTALL[*]}${NC}"
            fi
        else
            echo -e "${BLUE}  Would install: ${DEPS_TO_INSTALL[*]}${NC}"
        fi
    fi
fi

# Create install directory
if [ "$INSTALL_SCOPE" = "global" ]; then
    sudo mkdir -p "$INSTALL_DIR"
else
    mkdir -p "$INSTALL_DIR"
fi

# Create tool wrapper function
create_tool_wrapper() {
    local tool_name="$1"
    local tool_script="$2"
    
    if [ ! -f "$SCRIPT_ROOT/$tool_script" ]; then
        echo -e "${YELLOW}  ⚠️  $tool_name not found at $SCRIPT_ROOT/$tool_script, skipping${NC}"
        return
    fi
    
    local wrapper_content="#!/bin/bash
# IntermCLI $tool_name wrapper
SCRIPT_ROOT=\"$SCRIPT_ROOT\"
TOOL_PATH=\"\$SCRIPT_ROOT/$tool_script\"

if [ -f \"\$TOOL_PATH\" ]; then
    python3 \"\$TOOL_PATH\" \"\$@\"
else
    echo \"❌ $tool_name tool not found at \$TOOL_PATH\"
    exit 1
fi"
    
    if [ "$INSTALL_SCOPE" = "global" ]; then
        echo "$wrapper_content" | sudo tee "$INSTALL_DIR/$tool_name" > /dev/null
        sudo chmod +x "$INSTALL_DIR/$tool_name"
    else
        echo "$wrapper_content" > "$INSTALL_DIR/$tool_name"
        chmod +x "$INSTALL_DIR/$tool_name"
    fi
    
    INSTALLED_FILES+=("$INSTALL_DIR/$tool_name")
    echo -e "${GREEN}  ✅ $tool_name${NC}"
}

# Install tools
echo -e "${BLUE}🔧 Installing tools...${NC}"
create_tool_wrapper "scan-ports" "tools/scan-ports/scan-ports.py"
# FIX: Use the correct filename for find-projects
create_tool_wrapper "find-projects" "tools/find-projects/find-projects.py"

# PATH check
echo ""
echo -e "${BLUE}🛤️  Checking PATH configuration...${NC}"
if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
    echo -e "${GREEN}  ✅ $INSTALL_DIR is in PATH${NC}"
else
    echo -e "${YELLOW}  ⚠️  $INSTALL_DIR is not in PATH${NC}"
    echo -e "${YELLOW}     Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):${NC}"
    echo -e "${BLUE}     export PATH=\"$INSTALL_DIR:\$PATH\"${NC}"
    
    if ask_yes_no "Add to PATH automatically?" "y"; then
        SHELL_RC=$(detect_shell_profile)
        
        if [ -n "$SHELL_RC" ]; then
            echo "" >> "$SHELL_RC"
            echo "# IntermCLI PATH" >> "$SHELL_RC"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
            echo -e "${GREEN}  ✅ Added to $SHELL_RC${NC}"
            echo -e "${YELLOW}     Restart your terminal or run: source $SHELL_RC${NC}"
        else
            echo -e "${YELLOW}  ⚠️  Cannot detect shell, please add manually${NC}"
        fi
    fi
fi

# VERIFY INSTALLATION
verify_installation

# Installation complete
echo ""
echo -e "${GREEN}✅ IntermCLI installation complete!${NC}"
echo ""
echo -e "${BLUE}🚀 Quick start:${NC}"
echo -e "  ${GREEN}scan-ports localhost${NC}        # Scan local ports"
echo -e "  ${GREEN}find-projects${NC}               # Find development projects"
echo -e "  ${GREEN}find-projects --config${NC}      # View configuration"
echo ""
echo -e "${BLUE}⚙️  Configuration:${NC}"
echo -e "  ${GREEN}$CONFIG_DIR/config.toml${NC}"
echo ""
echo -e "${BLUE}🗑️  To uninstall:${NC}"
echo -e "  ${GREEN}$0 --uninstall${NC}"