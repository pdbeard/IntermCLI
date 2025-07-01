# 🏗️ IntermCLI Architecture

## Overview

IntermCLI is designed as a collection of independent, self-contained terminal utilities that can optionally share common functionality when it makes sense. Each tool is designed to work standalone while benefiting from shared infrastructure for dependency management, configuration, and documentation.

## 📁 Project Structure

```
intermcli/
├── README.md                  # Project overview, quick start
├── LICENSE                    # GPL v3
├── CHANGELOG.md               # Version history for entire suite
├── requirements.txt           # Optional dependencies for all tools
├── requirements-dev.txt       # Development dependencies
├── install.sh                 # Installation script for all tools (requirements.txt only)
├── todo                       # Development todo list
├── .gitignore
├── .github/                   # GitHub-specific files
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows_future/      # Future GitHub Actions (not active yet)
├── docs/                      # Suite-wide documentation
│   ├── DESIGN.md              # Overall design philosophy
│   ├── CONTRIBUTING.md        # How to contribute to any tool
│   ├── ARCHITECTURE.md        # This document
│   ├── CONFIGURATION.md       # Comprehensive config documentation
│   ├── commands/              # Command-specific documentation
│   │   ├── scan-ports.md
│   │   └── find-projects.md
│   ├── tools/                 # Individual tool documentation
│   │   ├── scan-ports.md
│   │   ├── find-projects.md
│   │   └── tool-template.md   # Template for new tools
│   └── examples/              # Cross-tool usage examples
│       ├── basic-usage.md
│       └── workflow-examples.md
├── tools_manifest.toml        # Tool manifest for modular install/discovery
├── tools/                     # Independent tool implementations
│   ├── scan-ports/
│   │   ├── scan-ports.py      # Main executable
│   │   ├── config/
│   │   │   └── defaults.toml  # Tool-specific config (TOML)
│   │   └── README.md          # Tool-specific docs
│   ├── find-projects/
│   │   ├── find-projects.py   # Main executable
│   │   ├── config/
│   │   │   └── defaults.toml  # Tool-specific config (TOML)
│   │   └── README.md          # Tool-specific docs
│   └── template-tool/         # Template for new tools
│       ├── action-target.py   # Template executable
│       └── README.md
├── shared/                    # Shared utilities (minimal, TOML-focused)
│   ├── __init__.py
│   ├── config_loader.py       # Common TOML config loading patterns
│   ├── enhancement_loader.py  # Progressive enhancement helpers
│   └── network_utils.py       # Common network utilities
├── bin/                       # Executable entry points
│   ├── scan-ports             # Wrapper to tools/scan-ports/scan-ports.py
│   ├── find-projects          # Wrapper to tools/find-projects/find-projects.py
│   ├── interm                 # Optional unified dispatcher
│   └── install-tool           # Script to add new tools
└── tests/                     # Suite-wide integration tests (planned)
```

## 🎯 Core Architecture Principles

### 1. Tool Independence First

Each tool in [`tools/`](tools/) is designed to be:
- **Self-contained**: Can run with just its own directory
- **Independently testable**: Has its own test suite
- **Minimally coupled**: Uses shared utilities only when there's clear benefit
- **Separately documented**: Complete documentation in its README

**Current Status**: Both [`scan-ports`](tools/scan-ports/) and [`find-projects`](tools/find-projects/) follow this pattern.

### 2. Action-Target Naming Convention

All tools follow the `action-target` pattern:
- **scan-ports** - Scans network ports for services
- **find-projects** - Finds and navigates development projects

### 3. Progressive Sharing

Shared utilities are created only when:
- Multiple tools implement the same pattern
- There's clear benefit to consolidation
- The abstraction is stable and well-defined

**Current Status**: Shared utilities directory exists with TOML config loading helpers and other minimal abstractions.

### 4. TOML-Only Configuration

- All configuration files use TOML format for readability, comments, and maintainability.
- The configuration hierarchy is:
    1. Tool defaults (`tools/{tool}/config/defaults.toml`)
    2. User global config (`~/.config/intermcli/config.toml`)
    3. User tool-specific config (`~/.config/intermcli/{tool}.toml`)
    4. Project local config (`.intermcli.toml`)
    5. Environment variables
    6. Command line arguments

- The tool manifest (`tools_manifest.toml`) is the source of truth for installed/discoverable tools.

### 5. Installation and Tool Discovery

- The `install.sh` script reads `tools_manifest.toml` to install and register tools.
- Each tool is installed as a standalone executable in the user's PATH.
- The manifest enables modular installation and future plugin support.

## 🔧 Tool Development Pattern

### Tool Structure Example

**scan-ports**:
```
tools/scan-ports/
├── scan-ports.py
├── config/
│   └── defaults.toml
└── README.md
```

**find-projects**:
```
tools/find-projects/
├── find-projects.py
├── config/
│   └── defaults.toml
└── README.md
```

### Configuration Strategy

- All configuration is TOML-based.
- Shared utilities in `shared/config_loader.py` provide config loading and precedence logic.
- Tools should document their config structure in their README and provide a `defaults.toml`.

## 🚀 Installation & Usage

### Installation Process

```bash
# Main installation script
./install.sh

# Creates wrappers in ~/.local/bin/
# scan-ports → tools/scan-ports/scan-ports.py
# find-projects → tools/find-projects/find-projects.py
```

### Usage Patterns

**Scan Ports**:
```bash
scan-ports localhost
```

**Find Projects**:
```bash
find-projects
```

**Configuration Management**:
```bash
# View and modify configuration (future)
interm config show
interm config set scan-ports.connection_timeout 5
interm config validate
```

## 🧪 Testing Strategy

- Each tool should have its own tests (unit/integration).
- Suite-level integration tests planned in `tests/`.
- Configuration loading and precedence should be tested using TOML files.
- Type safety and config validation are encouraged.

## 🔮 Future Evolution

### Roadmap

1. **Phase 1**: All tools use TOML config and follow action-target structure.
2. **Phase 2**: Expand shared utilities for TOML config and enhancement detection.
3. **Phase 3**: Implement comprehensive testing and config validation.
4. **Phase 4**: Add plugin architecture for third-party tools.

### When to Refactor

Extract to [`shared/`](shared/) when:
- **3+ tools** implement the same pattern
- **Clear abstraction** emerges naturally  
- **Maintenance burden** of duplication becomes significant

---

This architecture embraces the "start simple, evolve naturally" philosophy while maintaining clear migration paths toward a comprehensive configuration system and target structure.