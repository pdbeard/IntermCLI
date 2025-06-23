# 🏗️ IntermCLI Architecture

## Overview

IntermCLI is designed as a collection of independent, self-contained terminal utilities that can optionally share common functionality when it makes sense. Each tool is designed to work standalone while benefiting from shared infrastructure for dependency management, configuration, and documentation.

## 📁 Project Structure

```
intermcli/
├── README.md                  # Project overview, quick start
├── LICENSE                    # GPL v3
├── CHANGELOG.md              # Version history for entire suite
├── requirements.txt          # Optional dependencies for all tools
├── requirements-dev.txt      # Development dependencies
├── install.sh               # Installation script for all tools
├── todo                     # Development todo list
├── .gitignore
├── .github/                 # GitHub-specific files
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows_future/    # Future GitHub Actions (not active yet)
├── docs/                    # Suite-wide documentation
│   ├── DESIGN.md           # Overall design philosophy
│   ├── CONTRIBUTING.md     # How to contribute to any tool
│   ├── ARCHITECTURE.md     # This document
│   ├── CONFIGURATION.md    # Comprehensive config documentation
│   ├── commands/           # Command-specific documentation
│   │   ├── port-scan.md
│   │   └── project-find.md
│   ├── tools/              # Individual tool documentation
│   │   ├── port-scanner.md
│   │   ├── project-finder.md
│   │   └── tool-template.md # Template for new tools
│   └── examples/           # Cross-tool usage examples
│       ├── basic-usage.md
│       └── workflow-examples.md
├── config/                 # Shared/global configuration
│   ├── defaults.conf       # Suite-wide defaults (legacy shell format)
│   ├── enhancement-deps.json # Optional dependency mappings
│   └── README.md          # Config system documentation
├── tools/                  # Independent tool implementations
│   ├── scan-ports/
│   │   ├── scan-ports.py   # Main executable
│   │   ├── config/
│   │   │   └── ports.json  # Tool-specific config
│   │   └── README.md       # Tool-specific docs
│   ├── find-projects/
│   │   ├── project-finder.py # Main executable (transitioning to find-projects.py)
│   │   └── README.md       # Tool-specific docs
│   └── template-tool/      # Template for new tools
│       ├── action-target.py # Template executable (corrected filename)
│       └── README.md
├── shared/                 # Shared utilities (placeholder structure)
│   ├── __init__.py
│   ├── config_loader.py    # Common config loading patterns
│   ├── enhancement_loader.py # Progressive enhancement helpers
│   └── network_utils.py    # Common network utilities
├── bin/                    # Executable entry points
│   ├── scan-ports         # Wrapper to tools/scan-ports/scan-ports.py
│   ├── find-projects      # Project finder wrapper (new action-target name)
│   ├── pf                 # Legacy project finder wrapper (for compatibility)
│   ├── interm             # Optional unified dispatcher
│   └── install-tool       # Script to add new tools
└── tests/                  # Suite-wide integration tests (planned)
```

## 🎯 Core Architecture Principles

### 1. Tool Independence First

Each tool in [`tools/`](tools/) is designed to be:
- **Self-contained**: Can run with just its own directory
- **Independently testable**: Has its own test suite
- **Minimally coupled**: Uses shared utilities only when there's clear benefit
- **Separately documented**: Complete documentation in its README

**Current Status**: The [`scan-ports`](tools/scan-ports/) tool follows this pattern. The [`find-projects`](tools/find-projects/) tool is transitioning from the legacy `lib/` structure.

### 2. Action-Target Naming Convention

All tools follow the `action-target` pattern:
- **scan-ports** - Scans network ports for services
- **find-projects** - Finds and navigates development projects (migrating from `pf`)

**Legacy Migration**: The project finder is accessible via both [`bin/pf`](bin/pf) (legacy) and [`bin/find-projects`](bin/find-projects) (target) wrappers.

### 3. Progressive Sharing

Shared utilities are created only when:
- Multiple tools implement the same pattern
- There's clear benefit to consolidation
- The abstraction is stable and well-defined

**Current Status**: Shared utilities directory exists with placeholders, following the "start simple, evolve naturally" approach.

## 🔧 Tool Development Pattern

### Current Tool Structure

**scan-ports** (follows target structure):
```
tools/scan-ports/
├── scan-ports.py           # Main executable
├── config/
│   └── ports.json         # Comprehensive port definitions
└── README.md             # Tool documentation
```

**find-projects** (in transition):
```
tools/find-projects/
├── project-finder.py      # Current implementation
└── README.md             # Documentation placeholder
```

### Legacy Structure (being phased out)

The `lib/` directory pattern is being migrated:
- `lib/port-check.py` → [`tools/scan-ports/scan-ports.py`](tools/scan-ports/scan-ports.py) ✅ 
- `lib/project-finder.py` → [`tools/find-projects/find-projects.py`](tools/find-projects/find-projects.py) (in progress)

### Configuration Strategy

**Current Implementation**:
- Suite defaults: [`config/defaults.conf`](config/defaults.conf) (legacy shell-style format)
- Tool configs: [`tools/*/config/*.json`](tools/scan-ports/config/ports.json) (JSON format)
- Enhanced dependency mapping: [`config/enhancement-deps.json`](config/enhancement-deps.json)
- Tools handle their own config loading currently

**Target Configuration Hierarchy** (as documented in [CONFIGURATION.md](docs/CONFIGURATION.md)):
1. Suite defaults ([`config/defaults.json`](config/defaults.json) - target format)
2. Tool defaults ([`tools/tool-name/config/defaults.json`](tools/scan-ports/config/ports.json))
3. User global (`~/.config/intermcli/config.json`)
4. User tool-specific (`~/.config/intermcli/tool-name.json`)
5. Project local (`.intermcli.json`)
6. Command line arguments

**Configuration Features**:
- **JSON Schema Validation**: All config files validated against defined schemas
- **Progressive Enhancement**: Optional dependencies unlock advanced features
- **Security Settings**: Rate limiting, host restrictions, secure temp files
- **Editor Integration**: Auto-detection and configuration for multiple editors
- **Project Type Detection**: Comprehensive project indicators with priorities and icons

## 🚀 Installation & Usage

### Current Installation Process

```bash
# Main installation script
./install.sh

# Creates wrappers in ~/.local/bin/
# scan-ports → tools/scan-ports/scan-ports.py
# find-projects → tools/find-projects/project-finder.py
# pf → tools/find-projects/project-finder.py (legacy compatibility)
```

### Current Usage Patterns

**Scan Ports**:
```bash
# Direct execution (working)
python3 tools/scan-ports/scan-ports.py localhost

# Via wrapper (when properly set up)
scan-ports localhost
```

**Find Projects**:
```bash
# Current working methods
pf                         # Legacy wrapper (compatibility)
find-projects              # New action-target wrapper

# Target method (after migration)
find-projects              # Will use tools/find-projects/find-projects.py
```

**Configuration Management**:
```bash
# View and modify configuration
interm config show
interm config set scanner.enhanced_detection true
interm config validate

# Interactive setup
interm config init
```

## 🔄 Current Migration Tasks

### Immediate Priorities

1. **Complete find-projects migration**:
   ```bash
   # Move and rename
   mv tools/find-projects/project-finder.py tools/find-projects/find-projects.py
   
   # Update bin/pf and bin/find-projects to point to new location
   ```

2. **Standardize configuration format**:
   ```bash
   # Convert config/defaults.conf to config/defaults.json
   # Implement JSON schema validation
   # Populate empty README files
   ```

3. **Implement shared configuration utilities**:
   ```bash
   # Populate shared/config_loader.py with common patterns
   # Add configuration hierarchy support
   # Implement schema validation
   ```

4. **Update installation script**:
   ```bash
   # Update install.sh to create both find-projects and pf wrappers
   # Remove references to lib/ directory
   ```

### Configuration System Migration

| Component | Current Status | Target Status |
|-----------|----------------|---------------|
| Suite defaults | `defaults.conf` (shell) | `defaults.json` (JSON) |
| Schema validation | Not implemented | JSON Schema validation |
| Config commands | Documented only | `interm config` implementation |
| Hierarchy support | Tool-specific only | Full 6-level hierarchy |
| Security settings | Not implemented | Rate limiting, host restrictions |

### File Naming Corrections Made

| Documented | Actual | Status |
|------------|--------|---------|
| `port-scan.py` | `scan-ports.py` | ✅ Corrected |
| `project-find.py` | `project-finder.py` | 🔄 Needs rename to `find-projects.py` |
| `defaults.json` | `defaults.conf` | 🔄 Needs conversion |
| `workflows/` | `workflows_future/` | ✅ Corrected |
| `action-target.py` | `action-targer.py` | ✅ Corrected |

## 🧪 Testing Strategy

**Current Status**: No tests implemented yet, following rapid development approach.

**Planned Testing Structure**:
```bash
# Tool-level tests (future)
tools/scan-ports/tests/
tools/find-projects/tests/

# Suite-level tests (future)  
tests/test_integration.py
tests/test_shared.py
tests/test_config.py
```

**Configuration Testing**:
- Schema validation testing
- Configuration hierarchy precedence
- Security setting enforcement
- Cross-platform compatibility

## 🔮 Future Evolution

### Migration Roadmap

1. **Phase 1** (Current): Individual tools working independently with basic config
2. **Phase 2**: Migrate legacy `lib/` tools to [`tools/`](tools/) structure
3. **Phase 3**: Implement comprehensive configuration system
4. **Phase 4**: Extract common patterns to [`shared/`](shared/) utilities
5. **Phase 5**: Implement comprehensive testing
6. **Phase 6**: Plugin architecture for third-party tools

### Configuration Evolution

**Next Steps**:
- Convert [`config/defaults.conf`](config/defaults.conf) to JSON format
- Implement [`shared/config_loader.py`](shared/config_loader.py) with hierarchy support
- Add JSON schema validation
- Implement `interm config` command suite
- Add security and performance configuration options

### When to Refactor

Extract to [`shared/`](shared/) when:
- **3+ tools** implement the same pattern
- **Clear abstraction** emerges naturally  
- **Maintenance burden** of duplication becomes significant

**Configuration Sharing Triggers**:
- Multiple tools need identical config loading patterns
- Schema validation becomes tool-agnostic requirement
- User configuration management needs centralization

---

This architecture embraces the "start simple, evolve naturally" philosophy while maintaining clear migration paths toward a comprehensive configuration system and target structure.