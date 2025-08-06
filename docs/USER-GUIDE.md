# IntermCLI User Guide

Your quick-start reference for installing, configuring, and using IntermCLI tools for development and system administration.

This guide covers the essentials of installing and using IntermCLI tools.

## Installation

Quick installation:

```bash
git clone https://github.com/pdbeard/intermcli.git
cd intermcli
./install.sh
```

The installer will:
- Copy tools to `~/.local/bin/`
- Set up configuration files
- Offer to add the tools to your PATH
- Optionally install enhanced dependencies

## Available Tools

IntermCLI includes the following tools:

| Tool | Purpose | Basic Usage |
|------|---------|-------------|
| `scan-ports` | Network port scanner | `scan-ports hostname` |
| `find-projects` | Project discovery & navigation | `find-projects` |
| `sort-files` | File organization by type/date/size | `sort-files ~/Downloads` |
| `test-endpoints` | API testing tool | `test-endpoints https://api.example.com` |

## Core Concepts

### Configuration

All tools use TOML configuration files located in:
- `~/.config/intermcli/tool-name.toml` (user-specific)
- `.intermcli.toml` (project-specific)

### Progressive Enhancement

All tools offer:
- **Basic functionality**: Works with Python standard library
- **Enhanced features**: Available when optional dependencies are installed

## Tool Guides

### scan-ports

Scan local or remote hosts for open ports and detect running services.

```bash
# Basic usage
scan-ports localhost

# Scan specific ports
scan-ports -p 80,443,8080 example.com

# Use a predefined port list
scan-ports --list web myserver.local
```

### find-projects

Discover and navigate development projects.

```bash
# Interactive browser
find-projects

# Show configuration
find-projects --config
```

### sort-files

Organize files by type, date, or custom rules.

```bash
# Basic usage (organize by type)
sort-files ~/Downloads

# Sort by date
sort-files --by date ~/Documents

# Preview without changes
sort-files --dry-run ~/Desktop
```

### test-endpoints

Test API endpoints for availability and response.

```bash
# Basic test
test-endpoints https://api.example.com/v1/users

# Test with authentication
test-endpoints --auth token:xyz123 https://api.example.com/v1/users

# Run a suite of tests
test-endpoints --suite api-tests.json
```

## Tips and Tricks

- [ ] Use the `--help` flag with any tool for quick reference
- [ ] All tools support the `--version` flag to display version information
- [ ] Configuration files use TOML format for readability and consistency
- [ ] Set common environment variables for quick configuration:
    - `INTERMCLI_LOG_LEVEL`: Set logging detail (DEBUG, INFO, WARNING, ERROR)
    - `INTERMCLI_NO_COLOR`: Disable colored output (set to any value)

## Next Steps

- See each tool's README for tool-specific options
- Check the [Configuration Guide](CONFIGURATION.md) for detailed configuration options

<!-- Advanced Topics guide is not available. Add it when created. -->
