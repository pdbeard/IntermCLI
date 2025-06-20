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
│   ├── CONFIGURATION.md    # Shared config documentation
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
│   ├── defaults.conf       # Suite-wide defaults (currently .conf format)
│   ├── enhancement-deps.json # Optional dependency mappings (empty)
│   └── README.md          # Config system documentation (empty)
├── tools/                  # Independent tool implementations
│   ├── scan-ports/
│   │   ├── scan-ports.py   # Main executable
│   │   ├── config/
│   │   │   └── ports.json  # Tool-specific config
│   │   └── README.md       # Tool-specific docs (empty)
│   ├── find-projects/
│   │   ├── project-finder.py # Main executable (current implementation)
│   │   └── README.md       # Tool-specific docs (empty)
│   └── template-tool/      # Template for new tools
│       ├── action-targer.py # Template executable (note: typo in filename)
│       └── README.md
├── shared/                 # Shared utilities (placeholder structure)
│   ├── __init__.py
│   ├── config_loader.py    # Common config loading patterns (empty)
│   ├── enhancement_loader.py # Progressive enhancement helpers (empty)
│   └── network_utils.py    # Common network utilities (empty)
├── bin/                    # Executable entry points
│   ├── scan-ports         # Wrapper to tools/scan-ports/scan-ports.py (empty)
│   ├── pf                 # Project finder wrapper (active, points to lib/)
│   ├── interm             # Optional unified dispatcher (placeholder)
│   └── install-tool       # Script to add new tools (empty)
└── tests/                  # Suite-wide integration tests (not present yet)
```

## 🎯 Core Architecture Principles

### 1. Tool Independence First

Each tool in `tools/` is designed to be:
- **Self-contained**: Can run with just its own directory
- **Independently testable**: Has its own test suite
- **Minimally coupled**: Uses shared utilities only when there's clear benefit
- **Separately documented**: Complete documentation in its README

**Current Status**: The scan-ports tool follows this pattern. The find-projects tool is transitioning from the legacy `lib/` structure.

### 2. Action-Target Naming Convention

All tools follow the `action-target` pattern:
- **scan-ports** - Scans network ports for services
- **find-projects** - Finds and navigates development projects (migrating from `pf`)

**Legacy Migration**: The project finder is currently accessible via `pf` wrapper but should migrate to `find-projects` executable.

### 3. Progressive Sharing

Shared utilities are created only when:
- Multiple tools implement the same pattern
- There's clear benefit to consolidation
- The abstraction is stable and well-defined

**Current Status**: Shared utilities directory exists but is not yet populated, following the "start simple, evolve naturally" approach.

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
- `lib/port-check.py` → `tools/scan-ports/scan-ports.py` ✅ 
- `lib/project-finder.py` → `tools/find-projects/find-projects.py` (in progress)

### Configuration Strategy

**Current Implementation**:
- Suite defaults: `config/defaults.conf` (shell-style config)
- Tool configs: `tools/*/config/*.json` (JSON format)
- Tools handle their own config loading currently

**Target Implementation** (when shared utilities mature):
1. Suite defaults (`config/defaults.json`)
2. Tool defaults (`tools/tool-name/config/defaults.json`)
3. User global (`~/.config/intermcli/config.json`)
4. User tool-specific (`~/.config/intermcli/tool-name.json`)
5. Project local (`.intermcli.json`)
6. Command line arguments

## 🚀 Installation & Usage

### Current Installation Process

```bash
# Main installation script
./install.sh

# Creates wrappers in ~/.local/bin/
# scan-ports → tools/scan-ports/scan-ports.py
# pf → lib/project-finder.py (legacy)
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
# Current working method
pf                         # Uses legacy lib/project-finder.py

# Target method (future)
find-projects              # Will use tools/find-projects/find-projects.py
```

## 🔄 Current Migration Tasks

### Immediate Priorities

1. **Complete find-projects migration**:
   ```bash
   # Move and rename
   mv tools/find-projects/project-finder.py tools/find-projects/find-projects.py
   
   # Update bin/pf to point to new location
   # Create bin/find-projects wrapper
   ```

2. **Fix template tool**:
   ```bash
   # Fix typo in template filename
   mv tools/template-tool/action-targer.py tools/template-tool/action-target.py
   ```

3. **Standardize configuration**:
   ```bash
   # Convert config/defaults.conf to config/defaults.json
   # Populate empty README files
   ```

4. **Update installation script**:
   ```bash
   # Update install.sh to create find-projects wrapper
   # Remove references to lib/ directory
   ```

### File Naming Corrections Made

| Documented | Actual | Status |
|------------|--------|---------|
| `port-scan.py` | `scan-ports.py` | ✅ Corrected |
| `project-find.py` | `project-finder.py` | 🔄 Needs rename |
| `defaults.json` | `defaults.conf` | 🔄 Needs conversion |
| `workflows/` | `workflows_future/` | ✅ Corrected |
| `action-target.py` | `action-targer.py` | 🔄 Needs fix |

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
```

## 🔮 Future Evolution

### Migration Roadmap

1. **Phase 1** (Current): Individual tools working independently
2. **Phase 2**: Migrate legacy `lib/` tools to `tools/` structure
3. **Phase 3**: Extract common patterns to `shared/` utilities
4. **Phase 4**: Implement comprehensive testing
5. **Phase 5**: Plugin architecture for third-party tools

### When to Refactor

Extract to `shared/` when:
- **3+ tools** implement the same pattern
- **Clear abstraction** emerges naturally  
- **Maintenance burden** of duplication becomes significant

---

This architecture embraces the "start simple, evolve naturally" philosophy while maintaining clear migration paths toward the target structure.