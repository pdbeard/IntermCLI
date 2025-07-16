# 🖥️ IntermCLI

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos-lightgrey.svg)](https://github.com/pdbeard/intermcli)


<!-- CI Status -->
| Branch | Status |
|--------|--------|
| **main** | [![CI main](https://github.com/pdbeard/intermcli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pdbeard/intermcli/actions?query=branch%3Amain) |
| **dev**  | [![CI dev](https://github.com/pdbeard/intermcli/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/pdbeard/intermcli/actions?query=branch%3Adev) |


# 🖥️ IntermCLI

Interactive terminal utilities for developers. A suite of independent CLI tools for common developer and sysadmin tasks.

## Features
- Fast, self-contained CLI tools for port scanning, project discovery, file sorting, and endpoint testing
- Progressive enhancement: works with Python stdlib, optional dependencies add features
- Cross-platform: Linux and macOS

## Quick Start
```bash
git clone https://github.com/pdbeard/intermcli.git
cd intermcli
./install.sh
```
- Installs all tools to `~/.local/bin/`, sets up config, and offers to add to your PATH
- Optionally installs enhanced Python dependencies for extra features

## Tool Index
| Tool           | Description                        | Usage Doc                                      |
| -------------- | ---------------------------------- | ---------------------------------------------- |
| scan-ports     | Port scanner with service detection| [scan-ports README](tools/scan-ports/README.md) |
| find-projects  | Project discovery & navigation     | [find-projects README](tools/find-projects/README.md) |
| sort-files     | File organizer by type/date/size   | [sort-files README](tools/sort-files/README.md) |
| test-endpoints | API endpoint testing tool          | [test-endpoints README](tools/test-endpoints/README.md) |

## Documentation
- [Architecture](docs/ARCHITECTURE.md): Project structure and design principles
- [Contributing](docs/CONTRIBUTING.md): How to contribute, code style, PR workflow
- [Configuration](docs/CONFIGURATION.md): Config file locations and examples
- [Design Philosophy](docs/DESIGN.md): Naming conventions and project vision

## Branching Strategy  (not yet used)
Planned branching strategy for development and releases:

- **main**: Stable release branch. All production-ready code is merged here.
- **dev**: Active development branch. New features, fixes, and enhancements are merged here first.
- **feature/*, bugfix/*, enhancement/***: Short-lived branches for specific changes. Merge into `dev` via pull request.
- **release/***: (Optional) Used for preparing major releases.

**Workflow:**
1. Create a feature branch from `dev` (e.g., `feature/my-feature`).
2. Open a pull request to merge into `dev`.
3. After review and testing, changes are merged into `main` for release.
4. Branch protection rules may require PRs for changes to `main`.

See [Contributing](docs/CONTRIBUTING.md) for PR and code review details.

## License
GPL v3. See [LICENSE](LICENSE).

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

- **Python 3.9+** (tested on 3.9-3.11)
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


### CLI Tool Reference
- See the [CLI Tool Reference](docs/cli-tools.md) for a complete index of all available CLI tools and links to their documentation in each tool's directory.

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
