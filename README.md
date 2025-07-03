# 🖥️ IntermCLI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos-lightgrey.svg)](https://github.com/yourusername/intermcli)
[![CI](https://github.com/yourusername/intermcli/workflows/CI/badge.svg)](https://github.com/yourusername/intermcli/actions)

Interactive terminal utilities for developers. A collection of independent, self-contained CLI tools for common developer and sysadmin tasks.

## ✨ Features

- 🔍 **Port Scanner** (`scan-ports`) - Network port scanning with service detection
- 📁 **Project Finder** (`find-projects`) - Interactive git repository discovery and VS Code integration
- 🗃️ **Sort Files** (`sort-files`) - Organize directories by type, date, size, or custom rules
- 🔧 **Progressive Enhancement** - Core functionality works with Python standard library only
- 🚀 **Optional Dependencies** - Enhanced features with `requests`, `rich`, and other libraries
- 📊 **Rich Terminal Output** - Colorful, organized output when enhanced libraries are available

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/yourusername/intermcli.git
cd intermcli
./install.sh
```
- This will install all tools to `~/.local/bin/`, set up configuration, and offer to add to your PATH.
- You will be prompted to optionally install enhanced Python dependencies for extra features.

## 🛠️ Available Tools

### Port Scanner (`scan-ports`)
Advanced port scanner with progressive service detection.

```bash
scan-ports                    # Scan localhost with default ports
scan-ports 192.168.1.1       # Scan remote host
scan-ports --list web         # Scan only web service ports
scan-ports -p 3000,8080      # Scan specific ports
scan-ports --check-deps      # Show optional dependency status
```

**Features:**
- Configurable port lists (web, database, messaging, etc.)
- Service detection with HTTP header analysis
- Progressive enhancement (basic → enhanced with `requests`)
- Concurrent scanning for speed

### Project Finder (`find-projects`)
Interactive project discovery and navigation tool.

```bash
find-projects                # Launch interactive finder
find-projects --help         # Show all options
```

**Features:**
- Git repository discovery
- Interactive fuzzy search
- VS Code integration
- Project type detection and grouping

### Sort Files (`sort-files`)
Organize files in a directory by type, date, size, or custom rules.

```bash
sort-files ~/Downloads
sort-files --by type ~/Desktop
sort-files --by date --dry-run ~/Documents
sort-files --config ~/.config/intermcli/sort-files.toml ~/Downloads
```

**Features:**
- Sort by file type, date, or size
- Custom rules via TOML config (e.g., move `*-receipt.pdf` to `Receipts/`)
- Dry run mode for safe preview
- Safe by default (never overwrites files)
- Cross-platform (Linux, macOS)
- TOML-based configuration

## 🔧 Installation

For end users:
```bash
./install.sh
```
- This will install all tools to `~/.local/bin/`, set up configuration files, and offer to add to your PATH.
- The installer will prompt you to optionally install enhanced Python dependencies for extra features.

For developers:
```bash
pip3 install -r requirements-dev.txt  # Includes requirements.txt
```

### Manual Installation
Copy individual tools to your PATH and ensure they are executable.  
Optional features require manual installation of Python packages:

```bash
cp tools/scan-ports/scan-ports.py ~/.local/bin/scan-ports
cp tools/find-projects/find-projects.py ~/.local/bin/find-projects
cp tools/sort-files/sort-files.py ~/.local/bin/sort-files
chmod +x ~/.local/bin/scan-ports ~/.local/bin/find-projects ~/.local/bin/sort-files
pip3 install --user -r requirements.txt  # For enhanced features
```

### Optional Dependencies

The install script will detect and offer to install optional Python packages for enhanced features (e.g., `requests`, `rich`, `gitpython`).  
You can also install them manually:

```bash
pip3 install --user -r requirements.txt
```

### Development Tools

For development, install all dev dependencies:

```bash
pip3 install -r requirements-dev.txt
```

## 🎯 Requirements

- **Python 3.8+** (tested on 3.8-3.11)
- **Linux or macOS**
- Optional: Python packages in `requirements.txt` for enhanced features (installer will prompt)

## 📖 Usage Examples

<details>
<summary>Port Scanner Examples</summary>

```bash
# Basic scanning
scan-ports localhost
scan-ports 192.168.1.100

# Service-specific scanning
scan-ports --list web          # HTTP, HTTPS ports
scan-ports --list database     # MySQL, PostgreSQL, etc.
scan-ports --list messaging    # SMTP, IMAP, etc.

# Custom scanning
scan-ports -p 8000-8100        # Port range
scan-ports -p 3000,8080,9000   # Specific ports
scan-ports --timeout 5         # Custom timeout

# Enhanced mode (requires requests)
scan-ports --enhanced          # Detailed HTTP service detection
scan-ports --check-deps        # Show which enhancements are available
```
</details>

<details>
<summary>Project Finder Examples</summary>

```bash
# Interactive mode
find-projects                  # Launch TUI with fuzzy search

# Configuration
find-projects --config         # Edit search paths
```
</details>

<details>
<summary>Sort Files Examples</summary>

```bash
# Basic usage
sort-files ~/Downloads

# Sort by date
sort-files --by date ~/Documents

# Dry run (preview)
sort-files --dry-run ~/Downloads

# Use a custom config
sort-files --config ~/.config/intermcli/sort-files.toml ~/Downloads
```
</details>

## 🏗️ Architecture

IntermCLI follows a **tool-independent** architecture:

```
tools/
├── scan-ports/               # Independent port scanner
│   ├── scan-ports.py        # Main executable
│   ├── config/ports.json    # Tool-specific config
│   └── README.md
├── find-projects/           # Independent project finder
│   ├── find-projects.py    # Main executable
│   └── README.md
├── sort-files/              # Independent file organizer
│   ├── sort-files.py       # Main executable
│   ├── config/defaults.toml# Tool-specific config
│   └── README.md
└── shared/                  # Shared utilities (minimal)
    └── config_loader.py     # Common patterns only
```

**Design Principles:**
- **Independence**: Each tool works standalone
- **Progressive Enhancement**: Core features use stdlib, optional deps add enhancements
- **Consistent Naming**: Tools use a clear `verb-noun` pattern for discoverability
- **Minimal Shared Code**: Only when proven beneficial
- **Tool Manifest**: All tools are listed in `tools_manifest.toml` for modular installation and management.

## 📚 Documentation

- **[Design Philosophy](docs/DESIGN.md)** - Project vision and principles
- **[Architecture](docs/ARCHITECTURE.md)** - Technical structure and conventions
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute new tools or features
- **[Configuration](docs/CONFIGURATION.md)** - Config file reference and examples

### Tool-Specific Documentation
- **[Port Scanner](docs/tools/scan-ports.md)** - Detailed usage and configuration
- **[Project Finder](docs/tools/find-projects.md)** - Setup and customization
- **[Sort Files](docs/tools/sort-files.md)** - Usage and configuration

## 🤝 Contributing

We welcome contributions! Whether you want to:
- **Add a new tool** (please follow our naming and architecture conventions)
- **Enhance existing tools** with new features
- **Improve documentation** or fix bugs

Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) for details on:
- Tool development standards
- Testing requirements
- Pull request process

### Quick Contribution Guide
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Follow our naming conventions and architecture
4. Test with both minimal and full dependencies
5. Submit a pull request

## 🔄 Roadmap

### Planned Tools
- `check-services` - Enhanced service detection and analysis
- `list-processes` - Process monitoring and management
- `monitor-network` - Network traffic monitoring  
- `manage-configs` - Configuration file management
- `analyze-logs` - Log file analysis and filtering

### Current Focus
- Migrating existing tools to new architecture
- Establishing shared utility patterns
- Comprehensive testing across Python versions

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.