# CLI Tool Reference

This document provides an overview of all available CLI tools in the IntermCLI suite. Each tool has its own README with detailed documentation.

## Available Tools

| Tool Name      | Description                | Documentation Link                      |
| -------------- | ------------------------- | --------------------------------------- |
| Scan Ports     | Port scanning utility      | [scan-ports README](../tools/scan-ports/README.md) |
| Find Projects  | Project discovery utility  | [find-projects README](../tools/find-projects/README.md) |
| Sort Files     | File sorting utility       | [sort-files README](../tools/sort-files/README.md) |
| Test Endpoints | Endpoint testing utility   | [test-endpoints README](../tools/test-endpoints/README.md) |

## Features Overview

All tools in the IntermCLI suite share common features:

- **Consistent Interface**: All tools follow the same command-line argument structure
- **Shared Configuration**: TOML-based configuration with user and system defaults
- **Rich Output**: Color-coded, formatted output with fallbacks for basic terminals
- **Error Handling**: Consistent error messages and exit codes
- **Dry Run Mode**: Preview tool actions without making changes
- **Cross-Platform**: Works on Linux, macOS (and where applicable, Windows)

## Common Command Structure

```bash
tool-name [options] <target>
```

## Common Options

Most tools support the following options:
- `--help` - Show help information
- `--version` - Show version information
- `--config` - Specify a custom configuration file
- `--dry-run` - Preview actions without making changes

For tool-specific options, refer to the individual tool documentation linked above.
