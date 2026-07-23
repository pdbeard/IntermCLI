# find-projects

Interactive navigation tool for efficiently finding and opening development projects.

## Usage

```bash
# Launch interactive project browser
find-projects

# Display configuration information
find-projects --config

# Show version information
find-projects --version

# Search for specific project type
find-projects --type python
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--config` | `false` | Show configuration information and exit |
| `--version` | `false` | Show version information and exit |
| `--type` | None | Filter projects by type (python, js, go, etc.) |
| `--editor` | System default | Editor to open projects with (overrides config) |
| `--scan-only` | `false` | Scan and list projects without interactive mode |
| `--refresh` | `false` | Force refresh of project cache |

## Advanced Usage

For custom directory configuration and editor integration, see the [comprehensive documentation](../docs/tools/find-projects.md).

## Features

- Scans multiple directories for git repositories
- Fuzzy search and grouping by project type
- Open projects in your preferred editor (VS Code, Vim, etc.)
- Configurable via TOML and environment variables
- Secure scanning with symlink and path validation
- Fast concurrent directory scanning
- Project type detection based on files and structure
FIND_PROJECTS_DIRS=~/dev:~/src find-projects
FIND_PROJECTS_EDITOR=nvim find-projects
```

## Tips
- Use `/` to search, `t` to toggle grouping, arrow keys to navigate, and Enter to open a project.
- Ctrl+C exits or backs out of search mode.

## Requirements
- Python 3.9+
- Git repositories in your configured directories
- Optional: TOML config and enhanced editor support

---

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.
