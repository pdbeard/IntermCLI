## scan-ports

Scan local or remote hosts for open ports and detect running services. Supports configurable port lists, service detection, and both basic and enhanced detection modes.

### Usage

```bash
scan-ports localhost                # Scan localhost with default ports
scan-ports 192.168.1.1              # Scan remote host
scan-ports --list web               # Scan only web service ports
scan-ports -p 3000,8080             # Scan specific ports
scan-ports --show-lists             # Show available port lists
scan-ports --check-deps             # Show optional dependency status
```

### Features
- Configurable port lists via TOML
- Service detection (basic and enhanced)
- Fast concurrent scanning
- Progressive enhancement (works with stdlib, optional dependencies add features)
- Optional dependencies: requests, urllib3, tomli/tomllib
- Fully type-annotated with mypy support
- Comprehensive test coverage

### Configuration
- Port lists and categories are configured via TOML: `tools/scan-ports/config/ports.toml`
- You can add, remove, or customize port lists and service names.
- If TOML support is missing, a default set of common ports is used.

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
