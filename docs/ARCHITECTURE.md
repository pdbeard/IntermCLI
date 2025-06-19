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
├── .gitignore
├── .github/                 # GitHub-specific files
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/           # GitHub Actions
├── docs/                    # Suite-wide documentation
│   ├── DESIGN.md           # Overall design philosophy
│   ├── CONTRIBUTING.md     # How to contribute to any tool
│   ├── ARCHITECTURE.md     # This document
│   ├── CONFIGURATION.md    # Shared config documentation
│   ├── tools/              # Individual tool documentation
│   │   ├── port-scanner.md
│   │   ├── project-finder.md
│   │   └── tool-template.md # Template for new tools
│   └── examples/           # Cross-tool usage examples
│       ├── basic-usage.md
│       └── workflow-examples.md
├── config/                 # Shared/global configuration
│   ├── defaults.json       # Suite-wide defaults
│   ├── enhancement-deps.json # Optional dependency mappings
│   └── README.md          # Config system documentation
├── tools/                  # Independent tool implementations
│   ├── port-scanner/
│   │   ├── port-scan.py    # Main executable (your current lib/port-check.py)
│   │   ├── config/
│   │   │   └── ports.json  # Tool-specific config
│   │   ├── README.md       # Tool-specific docs
│   │   └── tests/          # Tool-specific tests (optional)
│   ├── project-finder/
│   │   ├── project-find.py # Main executable (your current lib/project-finder.py)
│   │   ├── config/
│   │   │   └── defaults.json
│   │   ├── README.md
│   │   └── tests/
│   └── template-tool/      # Template for new tools
│       ├── tool-name.py
│       ├── config/
│       ├── README.md
│       └── tests/
├── shared/                 # Shared utilities (only when proven needed)
│   ├── __init__.py
│   ├── config_loader.py    # Common config loading patterns
│   ├── enhancement_loader.py # Progressive enhancement helpers
│   └── network_utils.py    # Common network utilities
├── bin/                    # Executable entry points
│   ├── port-scan          # Symlink/wrapper to tools/port-scanner/port-scan.py
│   ├── project-find       # Symlink/wrapper to tools/project-finder/project-find.py
│   ├── interm             # Optional unified dispatcher
│   └── install-tool       # Script to add new tools
├── tests/                  # Suite-wide integration tests
│   ├── test_integration.py # Cross-tool workflows
│   ├── test_shared.py     # Shared utilities tests
│   └── fixtures/          # Common test data
└── examples/              # Example configurations and scripts
    ├── configs/           # Example config files
    ├── scripts/           # Usage examples
    └── workflows/         # Multi-tool workflow examples
```

## 🎯 Core Architecture Principles

### 1. Tool Independence First

Each tool in `tools/` is designed to be:
- **Self-contained**: Can run with just its own directory
- **Independently testable**: Has its own test suite
- **Minimally coupled**: Uses shared utilities only when there's clear benefit
- **Separately documented**: Complete documentation in its README

### 2. Progressive Sharing

Shared utilities are created only when:
- Multiple tools implement the same pattern
- There's clear benefit to consolidation
- The abstraction is stable and well-defined

```python
# Example: Only create shared/config_loader.py when 3+ tools need it
# Otherwise, each tool handles its own config loading
```

### 3. Unified Experience

Despite independence, tools provide consistent:
- Command-line interface patterns
- Configuration file formats  
- Error messaging and output
- Installation and update procedures

## 🔧 Tool Development Pattern

### Individual Tool Structure

Each tool follows this pattern:

```python
# tools/tool-name/tool-name.py
#!/usr/bin/env python3
"""
Standalone tool that can optionally use shared utilities.
"""
import sys
import os

# Add shared utilities to path if available
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'shared')
if os.path.exists(SHARED_DIR):
    sys.path.insert(0, SHARED_DIR)

# Core tool functionality (always works)
def core_functionality():
    """Tool's main logic using only stdlib"""
    pass

# Enhanced functionality (graceful degradation)
def enhanced_functionality():
    """Enhanced features with optional dependencies"""
    try:
        import requests  # or other optional deps
        # Enhanced implementation
    except ImportError:
        # Fallback to core functionality
        return core_functionality()

# Optional shared utility usage
def load_config():
    """Load configuration with optional shared utilities"""
    try:
        from config_loader import load_hierarchical_config
        return load_hierarchical_config(tool_name='tool-name')
    except ImportError:
        # Fallback to tool-specific config loading
        return load_tool_config()

if __name__ == '__main__':
    main()
```

### Configuration Strategy

**Hierarchical Loading (when shared/config_loader.py exists):**
1. Suite defaults (`config/defaults.json`)
2. Tool defaults (`tools/tool-name/config/defaults.json`)
3. User global (`~/.config/intermcli/config.json`)
4. User tool-specific (`~/.config/intermcli/tool-name.json`)
5. Project local (`.intermcli.json`)
6. Command line arguments

**Fallback Loading (when shared utilities not available):**
- Tool loads its own `config/defaults.json`
- Optionally checks for user config files
- Command line arguments override

### Dependency Management

**Suite-level dependencies (`requirements.txt`):**
```
# Optional enhancements for any tool
requests>=2.25.0
rich>=10.0.0
click>=8.0.0
```

**Tool-level dependency checking:**
```python
# In each tool
OPTIONAL_DEPS = {
    'requests': 'Enhanced HTTP detection',
    'rich': 'Beautiful terminal output',
    'click': 'Advanced CLI features'
}

def check_enhancements():
    """Report available/missing enhancements"""
    available = []
    missing = []
    
    for dep, description in OPTIONAL_DEPS.items():
        try:
            __import__(dep)
            available.append(f"✅ {dep}: {description}")
        except ImportError:
            missing.append(f"❌ {dep}: {description}")
    
    return available, missing
```

## 🚀 Installation & Usage

### Installation Process

```bash
# install.sh handles all tools
./install.sh

# Or install individual tools
./install.sh --tool port-scanner
./install.sh --tool project-finder
```

### Usage Patterns

**Individual tool usage:**
```bash
# Direct execution
./tools/port-scanner/port-scan.py localhost

# Via installed binary
port-scan localhost

# With global config
port-scan --config ~/.config/intermcli/port-scanner.json localhost
```

**Unified dispatcher (optional):**
```bash
# Via main entry point
interm port-scan localhost
interm project-find ~/dev

# List available tools
interm --list-tools

# Get help for specific tool
interm port-scan --help
```

## 🔄 Adding New Tools

### Tool Creation Process

1. **Copy template:**
   ```bash
   cp -r tools/template-tool tools/my-new-tool
   ```

2. **Implement tool logic:**
   - Core functionality in `tools/my-new-tool/my-new-tool.py`
   - Tool-specific config in `tools/my-new-tool/config/`
   - Documentation in `tools/my-new-tool/README.md`

3. **Add to suite:**
   - Update main `README.md` with tool description
   - Add tool documentation to `docs/tools/my-new-tool.md`
   - Create binary in `bin/my-new-tool`
   - Update `install.sh` to include new tool

4. **Optional shared utilities:**
   - Only extract to `shared/` if pattern used by 3+ tools
   - Update existing tools to use shared utility
   - Add tests for shared functionality

### Tool Requirements

Each tool must:
- Work standalone with Python stdlib
- Provide `--help` and `--version` flags
- Use consistent exit codes (0=success, 1=error, 2=invalid usage)
- Handle missing optional dependencies gracefully
- Include basic error handling and user feedback

## 🧪 Testing Strategy

### Multi-level Testing

**Tool-level tests:**
```bash
# Each tool can have its own tests
cd tools/port-scanner && python -m pytest tests/

# Or via main test runner
python -m pytest tools/port-scanner/tests/
```

**Suite-level tests:**
```bash
# Integration tests
python -m pytest tests/test_integration.py

# Shared utilities tests
python -m pytest tests/test_shared.py

# All tests
python -m pytest
```

### Testing Matrix

| Component | Tool Tests | Integration Tests | Shared Tests |
|-----------|------------|-------------------|--------------|
| Port Scanner | ✅ Core logic | ✅ CLI interface | N/A |
| Project Finder | ✅ Discovery logic | ✅ Editor integration | N/A |
| Config Loader | N/A | ✅ Cross-tool config | ✅ Shared utility |
| Install Script | N/A | ✅ Full installation | N/A |

## 🔮 Future Evolution

### When to Refactor

Extract to `shared/` when:
- **3+ tools** implement the same pattern
- **Clear abstraction** emerges naturally
- **Maintenance burden** of duplication becomes significant
- **User requests** for consistency across tools

### Plugin Architecture (Future)

Eventually, the tool-based architecture naturally supports plugins:

```
tools/
├── core-tools/          # Built-in tools
│   ├── port-scanner/
│   └── project-finder/
└── plugins/            # Third-party tools
    ├── git-tools/
    ├── docker-tools/
    └── custom-scanner/
```

### Migration Path

Current monolithic tools → Independent tools → Shared utilities → Plugin system

This evolution happens naturally as needs arise, rather than over-engineering upfront.

---

This architecture embraces the "start simple, evolve naturally" philosophy while maintaining the option for shared infrastructure when it proves valuable.