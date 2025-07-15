# 🛡️ scan-ports — Suite-Level Command Reference

`scan-ports` is part of the **IntermCLI** suite: a collection of modular, composable terminal tools for developers and sysadmins.
This document provides a centralized, suite-level overview of the `scan-ports` command, its options, features, and integration with the broader IntermCLI ecosystem.

---

## 🚀 Usage

```bash
scan-ports [OPTIONS] <host>
```

**Examples:**
```bash
scan-ports localhost
scan-ports 192.168.1.1
scan-ports example.com --port 22
scan-ports example.com --range 20 1024
scan-ports 10.0.0.1 --list web,database
scan-ports --list all localhost      # Scan all ports from every configured list
scan-ports --show-lists
scan-ports --check-deps
```

---

## ⚙️ Options

| Option                      | Description                                                        |
|-----------------------------|--------------------------------------------------------------------|
| `<host>`                    | Host to scan (IP or hostname)                                      |
| `-p, --port <PORT>`         | Check a specific port                                              |
| `-r, --range <START> <END>` | Scan a range of ports (e.g., `-r 1000 2000`)                       |
| `-l, --list <LISTS>`        | Scan ports from specific lists (comma-separated, e.g., `web,database`, or `all` for every list) |
| `--show-lists`              | Show available port lists and exit                                 |
| `--show-closed`             | Show closed ports in output                                        |
| `--no-service-detection`    | Disable service detection (faster scanning)                        |
| `--check-deps`              | Check optional dependency status and exit                          |
| `-t, --timeout <SECONDS>`   | Connection timeout in seconds (default: 3)                         |
| `--fast`                    | Fast scan with shorter timeout (sets timeout to 1s)                |
| `--threads <N>`             | Number of concurrent threads (default: 50)                         |
| `--help`                    | Show help message                                                  |

---

## 📝 Features

- **Fast multi-threaded scanning** (configurable thread count)
- **Configurable port lists** via TOML (`~/.config/intermcli/scan-ports.toml` or tool config)
- **Scan all lists at once** with `--list all`
- **Service detection**:
  - Basic (stdlib only)
  - Enhanced (with `requests`, `urllib3`, etc.)
- **HTTP/HTTPS detection**: banner, server, title, framework
- **Database and SSH detection**: version and banner grabbing
- **Scriptable output** (plain text, JSON planned)
- **Graceful error handling** and clear feedback
- **Optional TUI mode** (planned, with `rich`/`textual`)

---

## 🛠️ Configuration

You can customize port lists, timeouts, and detection settings in:

- `~/.config/intermcli/scan-ports.toml`
- Project-specific `.intermcli.toml`
- Tool directory: `tools/scan-ports/config/ports.toml`

**Example config:**
```toml
[port_lists.web]
description = "Web ports"
ports = { "80" = "HTTP", "443" = "HTTPS", "8080" = "HTTP Alt", "8443" = "HTTPS Alt" }

[port_lists.database]
description = "Database ports"
ports = { "5432" = "PostgreSQL", "3306" = "MySQL", "6379" = "Redis" }

[service_detection]
connection_timeout = 2
enhanced_detection = true
```

---

## 🔗 Integration with IntermCLI Suite

- **Consistent configuration:** All IntermCLI tools use TOML for configuration, supporting both global and tool-specific settings.
- **Composable workflows:** Output from `scan-ports` can be piped or integrated with other IntermCLI tools for automation and reporting.
- **Unified UX:** Shared conventions for options, output, and error handling across the suite.

---

## 🔒 Security Notes

- Only scan hosts/networks you own or have permission to test.
- Excessive scanning may trigger firewalls or IDS/IPS alerts.

---

## 🧩 Enhanced Features

If you have `requests`, `urllib3`, or other optional dependencies installed, you get:

- Enhanced HTTP/HTTPS detection (framework, server, redirects)
- Database version detection
- SSL/TLS certificate info (planned)
- Rich, colorized output (with `rich`)
- Interactive TUI mode (with `textual`, planned)

---

## 🐍 Requirements

- Python 3.8+
- No dependencies required for basic usage
- Optional: `requests`, `urllib3`, `rich`, `textual`, `tomli` (for Python <3.11)

---

## 📚 See Also

- [Configuration Reference](../CONFIGURATION.md)
- [Design Philosophy](../DESIGN.md)
- [Other IntermCLI Commands](../README.md)

---

## ❓ Troubleshooting

- **No results?** Check network/firewall settings and host reachability.
- **Permission denied?** Try running with elevated privileges for some ports.
- **Slow scans?** Increase timeout or scan fewer ports at a time.
- **TOML errors?** Install `tomli` if using Python <3.11.

---

Happy scanning!
