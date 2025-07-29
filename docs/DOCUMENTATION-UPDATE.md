# Documentation Updates

This file tracks significant documentation updates as the IntermCLI project evolves.

## July 29, 2025

### Configuration System Updates

- Updated documentation to reflect the improved configuration system.
- All tools now use a consistent configuration hierarchy:
  1. Command line arguments
  2. Environment variables
  3. Project config (`.intermcli.toml`)
  4. User tool-specific config (`~/.config/intermcli/{tool-name}.toml`)
  5. User global config (`~/.config/intermcli/config.toml`)
  6. Tool defaults (`tools/{tool-name}/config/defaults.toml`)

- Tools now utilize the shared ConfigLoader utility for consistent configuration handling.
- The `sort-files` tool has been updated to use its dedicated configuration file rather than hardcoded values.
- Configuration examples in documentation have been updated to reflect actual tool configurations.

### Tool-Specific Updates

- Updated `sort-files` README to document the configuration changes.
- Added information about configuration file precedence and fallbacks.
- Improved the integration example to demonstrate proper configuration file loading.

### Testing Framework

- Updated the testing framework (`test_tools.sh`) to support all tools.
- Added documentation about testing methodology and setup.

### Branching Strategy Updates

- Implemented a new branching strategy with `main` and `staging` branches.
- Updated all relevant documentation to reflect the new workflow:
  1. All development work occurs in feature branches created from `staging`
  2. Changes are merged into `staging` for testing and validation
  3. Stable `staging` code is promoted to `main` via pull request
  4. The `main` branch contains only production-ready code
- Updated CONTRIBUTING.md with detailed workflow instructions
- Added a Development Workflow section to ARCHITECTURE.md
- Removed references to the previous branching strategy

## How to Update Documentation

When making significant changes to the codebase, please update this file to help other contributors understand the evolution of the project. Documentation updates should include:

1. A description of the changes made
2. Which tools or components were affected
3. Any new patterns or conventions introduced
4. Any deprecated patterns or conventions

This helps maintain consistency across the project and ensures that all contributors are aware of the current best practices.
