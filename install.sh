#!/bin/bash
set -e
set -u
set -o pipefail

# Colors FIRST (before any usage)
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Detect Python and pip (prefer venv if active)
if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON_BIN="$VIRTUAL_ENV/bin/python"
    PIP_BIN="$VIRTUAL_ENV/bin/pip"
else
    PYTHON_BIN="python3"
    PIP_BIN="pip3"
fi

# Things to have early
OPTIONAL_MISSING=()
SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_MANIFEST="$SCRIPT_ROOT/tools_manifest.toml"
INSTALL_OPTIONAL=false


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


if [ ! -f "$TOOLS_MANIFEST" ]; then
    echo -e "${RED}❌ tools_manifest.toml not found at $TOOLS_MANIFEST${NC}"
    exit 1
fi

parse_tools() {
    python3 -c "
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib
try:
    with open('$TOOLS_MANIFEST', 'rb') as f:
        data = tomllib.load(f)
    for tool in data['tool']:
        print(f\"{tool['name']}|{tool['script']}|{tool.get('is_executable', False)}\")
except Exception as e:
    print('Error parsing tools_manifest.toml:', e, file=sys.stderr)
    sys.exit(1)
"
}

verify_installation() {
    echo -e "${BLUE}🔍 Verifying installation...${NC}"
    parse_tools | while IFS="|" read -r tool_name _ _; do
        if [ -f "$INSTALL_DIR/$tool_name" ] && [ -x "$INSTALL_DIR/$tool_name" ]; then
            echo -e "${GREEN}  ✅ $tool_name installed and executable${NC}"
        else
            echo -e "${RED}  ❌ $tool_name installation failed${NC}"
            return 1
        fi

        if command -v "$tool_name" >/dev/null 2>&1; then
            echo -e "${GREEN}  ✅ $tool_name is in PATH${NC}"
        else
            echo -e "${YELLOW}  ⚠️  $tool_name not in PATH${NC}"
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
        # Temporarily disable set -e for read
        set +e
        read -r -p "$prompt" response
        local read_exit_code=$?
        set -e

        if [ $read_exit_code -ne 0 ]; then
            echo ""
            echo -e "${YELLOW}Installation cancelled by user${NC}"
            exit 130
        fi

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
if [ $# -eq 0 ] || [ "$1" = "install" ]; then
    echo "IntermCLI Installation Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install, -i  Install IntermCLI tools"
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

# Check for pip3
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 not found${NC}"
    exit 1
fi

# Uninstall section: remove all tools from manifest
if [ "$1" = "--uninstall" ]; then
    echo -e "${BLUE}🗑️  Uninstalling IntermCLI...${NC}"
    if ask_yes_no "Remove installed tools?" "y"; then
        parse_tools | while IFS="|" read -r tool_name _ _; do
            rm -f "$HOME/.local/bin/$tool_name"
            echo -e "${GREEN}  ✅ $tool_name removed${NC}"
        done
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

INSTALLED_FILES=()
INSTALLED_DIRS=()

# Add logging capability
CONFIG_DIR="$HOME/.config/intermcli"
LOG_FILE="$CONFIG_DIR/install.log"

# Ensure config dir exists before logging
mkdir -p "$CONFIG_DIR"
: > "$LOG_FILE"

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

OPTIONAL_MISSING=()
if [ "$NEEDS_TOMLI" = true ]; then
    OPTIONAL_MISSING+=("tomli")
fi

if [ -f "$SCRIPT_ROOT/requirements.txt" ]; then
    echo -e "${BLUE}  Reading requirements.txt...${NC}"
    TEMP_FILE=$(mktemp -t intermcli.XXXXXX)
    "$PYTHON_BIN" -c "
import sys
import re

with open('$SCRIPT_ROOT/requirements.txt', 'r') as f:
    lines = f.readlines()

missing_deps = []
available_deps = []

for line in lines:
    line = line.strip()
    if not line or line.startswith('#') or line.startswith('-r'):
        continue
    if ';' in line:
        pkg_part, condition_part = line.split(';', 1)
        pkg_part = pkg_part.strip()
        condition_part = condition_part.strip()
        if 'python_version' in condition_part:
            if 'python_version < \"3.11\"' in condition_part:
                if sys.version_info >= (3, 11):
                    continue
            elif 'python_version >= \"3.11\"' in condition_part:
                if sys.version_info < (3, 11):
                    continue
    else:
        pkg_part = line
    pkg_name = re.split(r'[><=!]', pkg_part)[0].strip()
    try:
        __import__(pkg_name.replace('-', '_'))
        available_deps.append(pkg_name)
    except ImportError:
        missing_deps.append(pkg_name)

for pkg in available_deps:
    print(f'  ✅ {pkg}')
for pkg in missing_deps:
    print(f'  ⚪ {pkg} - optional')
with open('$TEMP_FILE', 'w') as f:
    f.write('\n'.join(missing_deps))
"    
    OPTIONAL_MISSING+=($(cat "$TEMP_FILE" 2>/dev/null || true))
    rm -f "$TEMP_FILE"
else
    echo -e "${YELLOW}  ⚠️  requirements.txt not found${NC}"
fi

INSTALL_OPTIONAL=false
if [ ${#OPTIONAL_MISSING[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}📋 Optional Python packages not found:${NC}"
    for dep in "${OPTIONAL_MISSING[@]}"; do
        echo -e "    • $dep"
    done
    echo ""
    if ask_yes_no "Install optional Python dependencies for enhanced features?" "y"; then
        INSTALL_OPTIONAL=true
    else
        echo -e "${YELLOW}Some features may be unavailable without optional dependencies.${NC}"
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
if [ "$INSTALL_OPTIONAL" = true ]; then
    echo -e "  Optional dependencies: Will install"
else
    echo -e "  Optional dependencies: Skip"
fi

echo ""
if ! ask_yes_no "Proceed with installation?" "y"; then
    echo -e "${YELLOW}Installation cancelled${NC}"
    exit 0
fi

# Start installation
echo ""
echo -e "${BLUE}🚀 Starting installation...${NC}"

# Install optional dependencies if chosen
if [ "$INSTALL_OPTIONAL" = true ] && [ ${#OPTIONAL_MISSING[@]} -gt 0 ]; then
    echo -e "${BLUE}📦 Installing optional Python dependencies...${NC}"
    if [ "$DRY_RUN" = false ]; then
        # Use --user only if not in venv
        if [ -n "$VIRTUAL_ENV" ]; then
            if "$PIP_BIN" install "${OPTIONAL_MISSING[@]}"; then
                echo -e "${GREEN}  ✅ Optional dependencies installed in venv${NC}"
            else
                echo -e "${YELLOW}  ⚠️  Failed to install some packages in venv${NC}"
                echo -e "${YELLOW}     Manual install: $PIP_BIN install ${OPTIONAL_MISSING[*]}${NC}"
            fi
        else
            if "$PYTHON_BIN" -m pip install --user "${OPTIONAL_MISSING[@]}"; then
                echo -e "${GREEN}  ✅ Optional dependencies installed${NC}"
            else
                echo -e "${YELLOW}  ⚠️  Failed to install some packages${NC}"
                echo -e "${YELLOW}     Manual install: $PYTHON_BIN -m pip install --user ${OPTIONAL_MISSING[*]}${NC}"
            fi
        fi
    else
        echo -e "${BLUE}  Would install: ${OPTIONAL_MISSING[*]}${NC}"
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
parse_tools | while IFS="|" read -r tool_name tool_script is_executable; do
    # Use case-insensitive check for is_executable
    if [ "$(echo "$is_executable" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
        if [ -f "$SCRIPT_ROOT/$tool_script" ]; then
            if [ "$INSTALL_SCOPE" = "global" ]; then
                sudo cp "$SCRIPT_ROOT/$tool_script" "$INSTALL_DIR/$tool_name"
                sudo chmod +x "$INSTALL_DIR/$tool_name"
            else
                cp "$SCRIPT_ROOT/$tool_script" "$INSTALL_DIR/$tool_name"
                chmod +x "$INSTALL_DIR/$tool_name"
            fi
            INSTALLED_FILES+=("$INSTALL_DIR/$tool_name")
            echo -e "${GREEN}  ✅ $tool_name (suite entry point)${NC}"
        else
            echo -e "${YELLOW}  ⚠️  $tool_name not found at $SCRIPT_ROOT/$tool_script, skipping${NC}"
        fi
    else
        create_tool_wrapper "$tool_name" "$tool_script"
    fi
done

# PATH check (improved)
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
            if ! grep -q "export PATH=\"$INSTALL_DIR" "$SHELL_RC"; then
                echo "" >> "$SHELL_RC"
                echo "# IntermCLI PATH" >> "$SHELL_RC"
                echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$SHELL_RC"
                echo -e "${GREEN}  ✅ Added to $SHELL_RC${NC}"
                echo -e "${YELLOW}     Restart your terminal or run: source $SHELL_RC${NC}"
            else
                echo -e "${YELLOW}  ⚠️  PATH already set in $SHELL_RC${NC}"
            fi
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
echo -e "${BLUE}📝 Install log: $LOG_FILE${NC}"
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