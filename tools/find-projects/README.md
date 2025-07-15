# find-projects

Interactive development project discovery and navigation. Scan configured directories for git repositories, group and search projects, and open them in your preferred editor.

## Usage

```bash
find-projects                # Launch interactive project browser
find-projects --config       # Show configuration information
find-projects --version      # Show version information
```

## Features
- Scans multiple directories for git repositories
- Fuzzy search and grouping by project type
- Open projects in your preferred editor (VS Code, Vim, etc.)
- Configurable via TOML and environment variables
- Secure scanning (symlink and path validation)
- Fast, concurrent directory scanning

## Configuration
- Uses TOML config at `tools/find-projects/config/defaults.toml`
- Override directories with `FIND_PROJECTS_DIRS` environment variable (colon-separated)
- Set default editor with `FIND_PROJECTS_EDITOR` environment variable
- For Python < 3.11, install `tomli` for TOML support: `pip install tomli`

## Example
```bash
find-projects
find-projects --config
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
