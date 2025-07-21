# Changelog
All notable changes to IntermCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- TOML-based configuration system with hierarchical precedence
- Progressive enhancement with optional dependencies
- Error handling and graceful fallbacks

### Changed
- Standardized action-target naming convention across all tools
- Improved installation script with PATH management
- Consolidated documentation structure

### Fixed
- Configuration loading and precedence

## [1.0.0] - YYYY-MM-DD (Upcoming)
### Added
- Initial release of IntermCLI suite with four core tools:
  - scan-ports: Network port scanning with service detection
  - find-projects: Interactive project discovery and navigation
  - sort-files: File organization by type, date, and custom rules
  - test-endpoints: API testing and validation
- Installer script with dependency detection
- Suite-wide documentation and contributing guidelines
- TOML configuration system with user and project overrides

### Changed
- Unified all tools under the action-target naming convention
- Standardized CLI argument patterns across tools
- Improved error handling and user feedback

### Deprecated
- Legacy individual tool scripts (now part of the unified suite)

## Tool-Specific Changes

### scan-ports
#### Added
- Service detection for HTTP, SSH, and database services
- Rich output with enhanced dependency detection
- Configurable port lists via TOML

### find-projects
#### Added
- Interactive fuzzy search interface
- Git repository detection and classification
- VS Code and editor integration

### sort-files
#### Added
- Sorting by type, date, and size
- Custom rule-based sorting via TOML configuration
- Safe mode with dry-run capability

### test-endpoints
#### Added
- Basic API endpoint testing
- Support for HTTP, HTTPS, and custom headers
- Response validation

[Unreleased]: https://github.com/pdbeard/intermcli/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pdbeard/intermcli/releases/tag/v1.0.0
