# ⚙️ IntermCLI Configuration

## Overview

IntermCLI uses a hierarchical configuration system for flexible customization. All config files use **TOML format** for readability and maintainability.

## 📁 Configuration File Locations

Configuration files are loaded in this order (higher overrides lower):

1. Tool defaults: `tools/{tool-name}/config/defaults.toml`
2. User global: `~/.config/intermcli/config.toml`
3. User tool-specific: `~/.config/intermcli/{tool-name}.toml`
4. Project local: `.intermcli.toml` (project root)
5. Environment variables: `TOOLNAME_SETTING=value`
6. Command line arguments

Example config directory:

```
~/.config/intermcli/
├── config.toml
├── scan-ports.toml
├── find-projects.toml
├── sort-files.toml
├── test-endpoints.toml
```

## 🔧 Tool Configuration (See per-tool README for full options)

- **Scan Ports**
  Default: `tools/scan-ports/config/defaults.toml`
  User: `~/.config/intermcli/scan-ports.toml`
  [Scan Ports README](../tools/scan-ports/README.md)
  ```toml
  [port_lists.web]
  description = "Web development ports"
  [port_lists.web.ports]
  "3000" = "React Dev"
  "3001" = "Next.js"
  ```

- **Find Projects**
  Default: `tools/find-projects/config/defaults.toml`
  User: `~/.config/intermcli/find-projects.toml`
  [Find Projects README](../tools/find-projects/README.md)
  ```toml
  development_dirs = ["~/development", "~/projects"]
  default_editor = "code"
  max_scan_depth = 3
  ```

- **Sort Files**
  Default: `tools/sort-files/config/defaults.toml`
  User: `~/.config/intermcli/sort-files.toml`
  [Sort Files README](../tools/sort-files/README.md)
  ```toml
  [sort]
  method = "name"
  ignore_hidden = true
  ```

- **Test Endpoints**
  Default: `tools/test-endpoints/config/defaults.toml`
  User: `~/.config/intermcli/test-endpoints.toml`
  [Test Endpoints README](../tools/test-endpoints/README.md)
  ```toml
  [endpoints]
  base_url = "http://localhost:8000"
  timeout = 5
  ```

## 🛠️ User & Project Config

- User global: `~/.config/intermcli/config.toml`
- Project: `.intermcli.toml` (project root)

Example:

```toml
[scan-ports]
default_host = "dev.myproject.com"
[find-projects]
development_dirs = ["./src", "./tools"]
```

## 🧩 Environment Variables

Each tool supports environment variable overrides. See per-tool README for details.

Example:

```bash
export SCAN_PORTS_HOST=localhost
export FIND_PROJECTS_EDITOR="nvim"
```

## 📊 Configuration Precedence

1. Command line arguments
2. Environment variables
3. Project config (`.intermcli.toml`)
4. User tool-specific config
5. User global config
6. Tool defaults

## 📝 TOML Format Examples

- Comments:

  ```toml
  # This is a comment
  default_editor = "code"
  ```

- Arrays:

  ```toml
  development_dirs = ["~/dev", "~/projects"]
  ```

- Nested sections:

  ```toml
  [port_lists.web]
  description = "Web ports"
  ```

## 🚀 Python TOML Support

- Python 3.11+: `import tomllib`
- Python <3.11: `pip install tomli`

---

## Advanced

# Tips, troubleshooting, and TOML details below

## 🔍 TOML Configuration Benefits

### Comments and Documentation

```toml
# This is a comment explaining the setting
default_editor = "code"

# Multi-line comments are supported
# You can document complex settings
# Like custom tmux session setups
complex_editor_command = """
tmux new-session -d -s project \; \
split-window -h \; \
send-keys 'vim .' Enter
"""
```

### Structured Data

```toml
# Nested sections are clean and readable
[port_lists.web]
description = "Web development ports"

[port_lists.web.ports]
"3000" = "React Dev"
"3001" = "Next.js"

# Arrays are simple
development_dirs = [
    "~/development",
    "~/projects",
    "~/code"
]
```

### Type Safety

```toml
# Numbers don't need quotes
max_scan_depth = 3
connection_timeout = 2.5

# Booleans are clear
enhanced_detection = true
show_closed_ports = false

# Strings are obvious
default_editor = "code"
```

## 🚀 TOML Requirements

### Python Dependencies

**Python 3.11+**: TOML support is built-in

```python
import tomllib  # Built into Python 3.11+
```

**Python < 3.11**: Install tomli

```bash
pip install tomli
```

### Tool Detection

Both tools automatically detect TOML support:

- ✅ Available: Uses TOML configuration files
- ❌ Missing: Falls back to default configuration with helpful error messages

```bash
# Check TOML support status
scan-ports --check-deps
find-projects --config
```

## 🔧 Configuration Commands (Future)

When the unified configuration system is implemented:

### View Configuration

```bash
# Show current effective configuration
interm config show
interm config show scan-ports
interm config show find-projects

# Show configuration sources and precedence
interm config sources scan-ports

# Validate TOML syntax
interm config validate
```

### Modify Configuration

```bash
# Set configuration value
interm config set scan-ports.connection_timeout 5
interm config set find-projects.default_editor "nvim"

# Add to arrays
interm config add find-projects.development_dirs ~/NewProjects

# Reset to defaults
interm config reset scan-ports
```

## 🔍 Troubleshooting Configuration

### Common Issues

1. **TOML support not available**

   ```bash
   # Check Python version
   python3 --version

   # Install tomli for Python < 3.11
   pip install tomli
   ```

2. **TOML syntax errors**

   ```bash
   # Tools will show syntax errors with line numbers
   scan-ports --check-config
   find-projects --config
   ```

3. **Configuration not loading**

   ```bash
   # Check file permissions
   ls -la ~/.config/intermcli/scan-ports.toml
   ls -la tools/scan-ports/config/defaults.toml
   ```

4. **Environment variables not working**

   ```bash
   # Check variable names (tool-specific prefixes)
   echo $SCAN_PORTS_TIMEOUT
   echo $FIND_PROJECTS_DIRS
   ```

### Debug Configuration Loading

```bash
# Enable debug output to see config loading process
scan-ports --debug localhost
find-projects --config  # Shows configuration details
```

---

This TOML-based configuration system provides better readability, comment support, and maintainability while maintaining the flexible hierarchical approach that allows users to customize IntermCLI tools to their specific needs and workflows.
