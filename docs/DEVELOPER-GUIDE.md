# IntermCLI Developer Guide

This guide provides a comprehensive overview of the IntermCLI project's architecture, design principles, and contribution workflow.

## Table of Contents
- [Project Overview](#project-overview)
- [Design Principles](#design-principles)
- [Project Structure](#project-structure)
- [Contribution Workflow](#contribution-workflow)
- [Code Style & Standards](#code-style--standards)
- [Testing Requirements](#testing-requirements)

## Project Overview

IntermCLI is an integrated ecosystem of CLI tools for developers and system administrators. The project combines the benefits of modular tool design with a shared foundation library that enables consistent user experience, simplified maintenance, and enhanced capabilities.

The core philosophy is **cohesive ecosystem with modular components**. Each tool follows the `action-target` naming pattern (e.g., `scan-ports`, `find-projects`) and leverages shared capabilities while focusing on its unique purpose.

> **Note**: See our [Design Vision](DESIGN-VISION.md) document for a complete overview of the project's design philosophy.

### Key Features

- Integrated ecosystem of CLI tools for port scanning, project discovery, file sorting, and endpoint testing
- Robust shared foundation for configuration, output formatting, and error handling
- Progressive enhancement: core functionality works with stdlib, optional dependencies add features
- Cross-platform: Linux and macOS

## Design Principles

### 1. Cohesive Ecosystem with Modular Components

Each tool in `tools/` is designed to be:
- **Purpose-focused**: Solves a specific problem for users
- **Modular**: Clear separation of concerns
- **Integrated**: Leverages shared capabilities
- **Consistently documented**: Complete documentation in its README

### 2. Action-Target Naming Convention

All tools follow the `action-target` pattern:
- **scan-ports** - Scans network ports for services
- **find-projects** - Finds and manages development projects
- **sort-files** - Organizes files by type/date/size
- **test-endpoints** - Tests API endpoints

This naming convention provides:
- Self-documenting commands
- Tab-completion friendliness
- Consistency across tools

### 3. Shared Foundation, Tool-Specific Extensions

- **Core Library**: Shared components in `shared/` directory:
  - Configuration management with TOML
  - Output formatting and color support
  - Error handling and logging
  - Argument parsing and validation
  - Network and file system utilities
- **Tool-Specific Logic**: Individual tools focus on their unique functionality

### 4. Progressive Enhancement Architecture

- **Essential Tier**: Core functionality using Python stdlib
- **Enhanced Tier**: Additional capabilities with optional dependencies
- **Advanced Tier**: Full-featured experience with complete dependency set
- **Clear Dependency Documentation**: Each feature indicates its requirements
- **Graceful Degradation**: Helpful fallbacks when dependencies are missing

### 5. Consistent User Experience

All tools use a consistent interface:
- Common argument patterns
- Standardized help documentation
- Consistent output formatting
- Clear error messaging
- Progress indicators when appropriate

### 6. Modular with Integration Points

- Each tool focuses on a specific task domain
- Tools can interoperate through common data formats
- Integration points allow tool composition
- Shared foundation enables consistency

## Project Structure

```
intermcli/
├── README.md            # Project overview, tool index, install
├── docs/                # Suite-level docs
│   ├── DESIGN-VISION.md # Core philosophy and architectural approach
│   └── DEVELOPER-GUIDE.md # Development guidelines and standards
├── tools/               # CLI tools within the ecosystem
│   ├── scan-ports/      # Port scanner tool
│   │   ├── scan-ports.py # Main executable
│   │   ├── config/      # Tool-specific configuration
│   │   └── README.md    # Tool documentation
│   ├── find-projects/   # Project discovery tool
│   ├── sort-files/      # File organizer tool
│   └── test-endpoints/  # API testing tool
├── shared/              # Shared foundation library
│   ├── config_loader.py # Configuration management
│   ├── output.py        # Consistent output formatting
│   ├── error_handler.py # Error handling utilities
│   ├── path_utils.py    # File system operations
│   └── network_utils.py # Network utilities
├── bin/                 # Executable wrappers for CLI tools
├── requirements*.txt    # Dependencies (main/dev)
├── install.sh           # Installer script
└── tools_manifest.toml  # Tool manifest for modular install/discovery
```

## Contribution Workflow

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch from `staging`:
   ```bash
   git checkout -b feature/my-feature staging
   ```
3. Add your tool in `tools/` with its own README and config
4. Add your tool to `tools_manifest.toml`
5. Test with both minimal and enhanced dependencies
6. Submit a PR to merge into the `staging` branch with a clear description

### Branching Strategy

- **main**: Stable release branch. Contains only production-ready, tested code.
- **staging**: Pre-production testing branch. All changes are merged here first for validation.
- **feature/*, bugfix/*, docs/*, hotfix/***: Short-lived branches for specific changes.

**Workflow:**
1. Create a feature branch from `staging` (e.g., `feature/my-feature`).
2. Open a pull request to merge into `staging`.
3. After review and testing in staging, changes are promoted to `main` via pull request.

### Adding a New Tool

When adding a new tool to the ecosystem, follow these guidelines:

- [ ] Create a new directory in `tools/` with a hyphenated name following the action-target pattern (e.g., `analyze-logs`)
- [ ] Include a main Python file with the same name (e.g., `analyze-logs.py`)
- [ ] Add a README.md with clear usage examples
- [ ] Create a `config/` subdirectory for tool-specific configuration files
- [ ] Add the tool to `tools_manifest.toml`
- [ ] Add tests in the `tests/` directory
- [ ] Leverage the shared foundation library:
    ```python
    # Import shared utilities
    from shared.config_loader import ConfigLoader
    from shared.output import Output, setup_tool_output
    from shared.error_handler import ErrorHandler

    # Use consistent patterns
    output = setup_tool_output("tool-name", log_level="INFO")
    config_loader = ConfigLoader("tool-name")
    error_handler = ErrorHandler(output)
    ```
- [ ] Implement progressive enhancement for optional dependencies
- [ ] Follow the consistent interface patterns

## Code Style & Standards

### Style Guidelines

- Use [black](https://github.com/psf/black) for formatting
- Use [isort](https://github.com/PyCQA/isort) for import sorting
- Use [ruff](https://github.com/astral-sh/ruff) for linting

### Pre-commit Hooks

Pre-commit hooks are configured in `.pre-commit-config.yaml` and run automatically before each commit:
- Formatting: black, isort
- Linting: ruff
- Whitespace, YAML, merge conflict, shebang, docstring, and secret checks

To enable:
```bash
pre-commit install
```

To run manually:
```bash
pre-commit run --all-files
```

### Documentation Standards

- [ ] Each tool should have its own README.md
- [ ] Use the [Output Style Guide](/docs/output-style-guide.md) for consistent user experience
- [ ] Include usage examples for common cases
- [ ] Document configuration options

## Testing Requirements

- [ ] All code should have appropriate tests
- [ ] Test with both minimal and optional dependencies
- [ ] Include unit and integration tests
- [ ] Test on Python 3.9+
- [ ] Use `pytest` and tools from `requirements-dev.txt`

### Running Tests

```bash
# Run all tests
pytest

# Run tests for a specific tool
pytest tests/scan_ports_test.py

# Run with coverage
pytest --cov=.
```
