# 🏗️ IntermCLI Architecture

## Overview

IntermCLI is a suite of independent CLI tools for developers and sysadmins. Each tool is standalone, with minimal shared code and simple configuration. The project is organized for clarity, modularity, and ease of contribution.

## Project Structure (Short Version)

```
intermcli/
├── README.md            # Project overview, tool index, install
├── docs/                # Suite-level docs (architecture, contributing, config, design)
├── tools/               # Individual CLI tools (each with its own README)
├── shared/              # Minimal shared utilities (config, enhancement, network)
├── bin/                 # Executable wrappers for CLI tools
├── requirements*.txt    # Dependencies (main/dev)
├── install.sh           # Installer script
├── tools_manifest.toml  # Tool manifest for modular install/discovery
├── .github/             # GitHub Actions, templates
├── todo                 # Development todo list
```

## Design Principles
- **Independence:** Each tool works standalone, with its own config and docs
- **Minimal Shared Code:** Only share code when it’s proven useful
- **Progressive Enhancement:** Core features use stdlib; optional deps add enhancements
- **Consistent Naming:** Tools use a clear `verb-noun` pattern
- **Modular Install:** All tools listed in `tools_manifest.toml` for easy management

## How to Contribute
- Add new tools in `tools/` with their own README and config
- Follow naming and architecture conventions
- See [CONTRIBUTING.md](CONTRIBUTING.md) for details
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
