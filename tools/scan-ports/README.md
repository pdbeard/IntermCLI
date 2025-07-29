# scan-ports

Port scanner that detects open ports and identifies running services on local or remote hosts.

## Usage

```bash
# Basic scanning
scan-ports localhost

# Scan remote host
scan-ports 192.168.1.1

# Scan specific port list
scan-ports --list web

# Scan custom ports
scan-ports -p 3000,8080

# View available port lists
scan-ports --show-lists

# Check optional dependencies
scan-ports --check-deps
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--list`, `-l` | `common` | Port list to scan (web, database, common, all) |
| `--ports`, `-p` | None | Comma-separated ports or ranges (e.g., 80,443,8000-8100) |
| `--timeout` | `1` | Connection timeout in seconds |
| `--threads` | `10` | Number of concurrent scanning threads |
| `--enhanced` | `false` | Use enhanced detection (requires requests) |
| `--show-lists` | `false` | Display available port lists and exit |
| `--check-deps` | `false` | Display optional dependency status and exit |

## Advanced Usage

For detailed port list configuration and custom service detection, see the [comprehensive documentation](../docs/tools/scan-ports.md).

## Features

- Configurable port lists via TOML configuration
- Basic and enhanced service detection modes
- Fast concurrent scanning with adjustable thread count
- Progressive enhancement with optional dependencies
- Support for CIDR notation for network scanning
- Fully type-annotated with mypy support
- Comprehensive test coverage

**Example TOML snippet:**
```toml
version = "1.0"

[port_lists.web]
description = "Web service ports"
[port_lists.web.ports]
80 = "HTTP"
443 = "HTTPS"
8080 = "HTTP Alt"
3000 = "Node.js Dev"
```

### Customizing
- Edit `ports.toml` to add new categories or ports.
- Use `scan-ports --show-lists` to view all available lists and their contents.
- Use `scan-ports -l <list_name>` to scan a specific category (e.g., `web`, `database`).

### Troubleshooting
- If you see "TOML support not available", install `tomli` for Python < 3.11: `pip install tomli`
- If the config file is missing, the tool will fall back to built-in defaults.
- For type checking during development, ensure you have `types-requests` and `types-urllib3` installed.

---
