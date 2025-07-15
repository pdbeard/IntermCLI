# 🗂️ find-projects — Suite-Level Command Reference

`find-projects` is an interactive terminal tool for discovering, searching, and opening your development projects.
It is part of the **IntermCLI** suite and follows the action-target naming and progressive enhancement conventions.

---

## 🚀 Usage

```bash
find-projects [OPTIONS]
```

**Examples:**
```bash
find-projects                # Launch interactive project browser
find-projects --config       # Show configuration and environment info
find-projects --version      # Show version information
```

---

## ⚙️ Options

| Option         | Description                                   |
|----------------|-----------------------------------------------|
| `--config`     | Show configuration debug info                 |
| `--version`    | Show version information                      |
| `-h, --help`   | Show help message                             |

---

## 📝 Features

- **Scans multiple directories** for Git repositories (configurable)
- **Fuzzy search** and instant filtering of projects
- **Group by project type** (Python, Node.js, Rust, etc.) or show recent
- **Open projects** in your preferred editor (configurable)
- **Keyboard navigation:**
  - Up/Down arrows: Move selection
  - `/`: Search
  - `t`: Toggle group by type
  - `Enter`: Open selected project
  - `q`: Quit
- **Security-aware:**
  - Validates editor commands
  - Skips unsafe symlinks
  - Limits scan depth and rate

---

## 🛠️ Configuration

- **TOML config:**
  - `tools/find-projects/config/defaults.toml` (default)
  - Override with environment variables

- **Environment variables:**
  - `FIND_PROJECTS_DIRS` — Colon-separated list of directories to scan
  - `FIND_PROJECTS_EDITOR` — Default editor command (default: `code`)

- **Configurable settings include:**
  - `development_dirs`: List of directories to scan
  - `default_editor`: Editor to open projects
  - `max_scan_depth`: How deep to scan for projects
  - `skip_dirs`: Directories to skip (e.g., `node_modules`, `.git`)
  - `max_projects`, `scan_timeout`, `allowed_editors`, etc.

---

## 🧩 Project Detection

- Finds projects by presence of a `.git` directory
- Detects project type by common marker files (e.g., `package.json`, `pyproject.toml`)
- Supports grouping and icons for major languages/frameworks

---

## 🖥️ Interactive UI

- Terminal-based, no GUI required
- Clean, scrollable project list with type icons and last modified dates
- Fuzzy search with instant results
- Open projects in your editor with a single keypress

---

## 🔒 Security Notes

- Only scans directories you configure or specify via environment
- Validates editor commands and skips unsafe symlinks
- Limits scan depth and rate to avoid excessive file operations

---

## 🐍 Requirements


- No dependencies required for basic usage
- For Python <3.11, install `tomli` for TOML config support:
  `pip install tomli`

---

## 📚 See Also

- [Configuration Reference](../CONFIGURATION.md)
- [Design Philosophy](../DESIGN.md)
- [Other IntermCLI Commands](../README.md)

---

## ❓ Troubleshooting

- **No projects found?**
  - Make sure your configured directories exist and contain Git repositories.
  - Use `FIND_PROJECTS_DIRS` to override directories if needed.
- **Editor not opening?**
  - Check that your editor is installed and in your PATH.
  - Use `FIND_PROJECTS_EDITOR` to set a different editor.
- **TOML errors?**
  - Install `tomli` if using Python <3.11.

---

Happy hacking!
