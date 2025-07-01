# ⚙️ IntermCLI Configuration

## Overview

IntermCLI uses a hierarchical configuration system that allows for flexible customization at multiple levels. Configuration files use **TOML format** for better readability, comment support, and maintainability.

## 📁 Configuration File Locations

Configuration files are loaded in the following priority order (later files override earlier ones):

1. **Tool Defaults** - `tools/{tool-name}/config/defaults.toml` (in repository)
2. **User Global Config** - `~/.config/intermcli/config.toml`
3. **User Tool-Specific** - `~/.config/intermcli/{tool-name}.toml`
4. **Project Local Config** - `.intermcli.toml` (in current directory)
5. **Environment Variables** - `TOOLNAME_SETTING=value`
6. **Command Line Arguments** - Override any config value

### Configuration Directory Structure

```
~/.config/intermcli/
├── config.toml          # Main user configuration
├── scan-ports.toml      # Port scanner specific settings
├── find-projects.toml   # Project finder specific settings
├── plugins/             # User plugins directory
└── cache/               # Cached data
```

## 🔧 Tool-Specific Configuration

### Scan Ports Configuration (`tools/scan-ports/config/defaults.toml`)

```toml
# Port scanning configuration
# Organized by service category for easy reference and scanning

[port_lists.common]
description = "Most commonly used development and service ports"

[port_lists.common.ports]
"22" = "SSH"
"80" = "HTTP"
"443" = "HTTPS"
"3000" = "Node.js/React Dev"
"3001" = "Node.js Alt"
"4000" = "Ruby/Jekyll"
"5000" = "Flask/Python Dev"
"8000" = "Django/Python Dev"
"8080" = "HTTP Alt/Tomcat"
"9000" = "SonarQube/PHP-FPM"
"5432" = "PostgreSQL"
"3306" = "MySQL/MariaDB"
"6379" = "Redis"
"27017" = "MongoDB"
"9200" = "Elasticsearch"
"5672" = "RabbitMQ"

[port_lists.web]
description = "Web development and HTTP services"

[port_lists.web.ports]
"80" = "HTTP"
"443" = "HTTPS"
"8080" = "HTTP Alt"
"8443" = "HTTPS Alt"
"3000" = "Node.js/React Dev"
"3001" = "Node.js Alt"
"4000" = "Ruby/Jekyll"
"5000" = "Flask Dev"
"8000" = "Django Dev"
"8888" = "Jupyter Notebook"
"9000" = "SonarQube"
"4200" = "Angular Dev"
"3030" = "Meteor Dev"
"8081" = "Tomcat Manager"
"9090" = "Prometheus"

[port_lists.database]
description = "Database services"

[port_lists.database.ports]
"3306" = "MySQL/MariaDB"
"5432" = "PostgreSQL"
"6379" = "Redis"
"27017" = "MongoDB"
"9200" = "Elasticsearch"
"9300" = "Elasticsearch Transport"
"5984" = "CouchDB"
"8086" = "InfluxDB"
"7000" = "Cassandra"
"7001" = "Cassandra SSL"
"9042" = "Cassandra CQL"
"1433" = "SQL Server"
"1521" = "Oracle DB"
"50000" = "DB2"

[port_lists.messaging]
description = "Message queues and streaming"

[port_lists.messaging.ports]
"5672" = "RabbitMQ"
"15672" = "RabbitMQ Management"
"9092" = "Kafka"
"2181" = "Zookeeper"
"4222" = "NATS"
"6222" = "NATS Cluster"
"8222" = "NATS Monitoring"
"1883" = "MQTT"
"8883" = "MQTT SSL"
"61613" = "ActiveMQ STOMP"
"61614" = "ActiveMQ WS"
"61616" = "ActiveMQ"

[port_lists.system]
description = "System and network services"

[port_lists.system.ports]
"22" = "SSH"
"21" = "FTP"
"23" = "Telnet"
"25" = "SMTP"
"53" = "DNS"
"67" = "DHCP Server"
"68" = "DHCP Client"
"110" = "POP3"
"143" = "IMAP"
"993" = "IMAP SSL"
"995" = "POP3 SSL"
"161" = "SNMP"
"162" = "SNMP Trap"
"389" = "LDAP"
"636" = "LDAP SSL"

[port_lists.docker]
description = "Docker and container services"

[port_lists.docker.ports]
"2375" = "Docker Daemon"
"2376" = "Docker Daemon SSL"
"2377" = "Docker Swarm"
"4789" = "Docker Overlay"
"7946" = "Docker Swarm"
"8080" = "Docker Registry"
"5000" = "Docker Registry"
"9000" = "Portainer"
"8000" = "Traefik Dashboard"
"9090" = "Prometheus"
"3000" = "Grafana"

[port_lists.security]
description = "Security and monitoring services"

[port_lists.security.ports]
"9200" = "Elasticsearch"
"5601" = "Kibana"
"8080" = "Jenkins"
"9000" = "SonarQube"
"3000" = "Grafana"
"9090" = "Prometheus"
"9093" = "Alertmanager"
"4317" = "OpenTelemetry"
"4318" = "OpenTelemetry HTTP"
"6831" = "Jaeger"
"14268" = "Jaeger"
"16686" = "Jaeger UI"

# Service detection settings
[service_detection]
connection_timeout = 5
read_timeout = 3
ssl_verify = false
follow_redirects = true
max_redirects = 3
detect_frameworks = true
extract_versions = true
user_agent = "scan-ports/1.0.0"
```

### Find Projects Configuration (`tools/find-projects/config/defaults.toml`)

```toml
# find-projects configuration

# Directories to scan for projects
development_dirs = [
    "~/development",
    "~/projects",
    "~/code",
    "~/workspace",
    "~/src"
]

# Default editor - can be any shell command
# Examples:
#   "code"                    # VS Code
#   "vim ."                   # Vim in current directory  
#   "~/scripts/dev-setup.sh"  # Custom script
#   "tmux new-session -d -s project \\; split-window -h \\; send-keys 'vim .' Enter"
default_editor = "code"

# Scan settings
max_scan_depth = 3

# Directories to ignore during scanning
skip_dirs = [
    ".git",
    "node_modules",
    ".vscode",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache"
]

# Project type detection
[project_types]
"Node.js" = { indicators = ["package.json", "package-lock.json", "yarn.lock"], icon = "🟨" }
"Python" = { indicators = ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"], icon = "🐍" }
"Rust" = { indicators = ["Cargo.toml"], icon = "🦀" }
"Go" = { indicators = ["go.mod", "go.sum"], icon = "🐹" }
"Java" = { indicators = ["pom.xml", "build.gradle", "build.gradle.kts"], icon = "☕" }
"PHP" = { indicators = ["composer.json"], icon = "🐘" }
"Ruby" = { indicators = ["Gemfile", "Gemfile.lock"], icon = "💎" }
"C++" = { indicators = ["CMakeLists.txt", "Makefile"], icon = "⚙️" }
"C#" = { indicators = [".csproj", ".sln"], icon = "🔷" }

# UI Settings
[ui]
show_icons = true
group_by_type_default = false
search_fuzzy = true
```

## 🔧 User Configuration Examples

### Basic User Config (`~/.config/intermcli/scan-ports.toml`)

```toml
# Custom port scanner configuration

# Override some common ports with custom descriptions
[port_lists.custom]
description = "My custom development ports"

[port_lists.custom.ports]
"3000" = "My React App"
"3001" = "My API Server"
"5432" = "Local PostgreSQL"
"6379" = "Local Redis"

# Service detection preferences
[service_detection]
connection_timeout = 2
enhanced_detection = true
```

### Advanced User Config (`~/.config/intermcli/find-projects.toml`)

```toml
# Custom project finder configuration

# My development directories
development_dirs = [
    "~/Code",
    "~/Work/projects",
    "~/OpenSource",
    "/workspace"
]

# Custom editor setup with tmux
default_editor = "tmux new-session -d -s dev \\; split-window -h \\; split-window -v \\; send-keys -t 0 'nvim .' Enter \\; send-keys -t 1 'git status' Enter \\; send-keys -t 2 'npm run dev' Enter \\; attach-session -t dev"

# Deeper scanning for complex projects
max_scan_depth = 5

# Additional directories to skip
skip_dirs = [
    ".git",
    "node_modules",
    ".vscode",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    "vendor",          # PHP
    "target",          # Rust/Java
    ".next",           # Next.js
    ".nuxt",           # Nuxt.js
    "coverage"         # Test coverage
]

# Custom project types
[project_types.Terraform]
indicators = ["*.tf", "terraform.tfvars"]
icon = "🏗️"

[project_types.Docker]
indicators = ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
icon = "🐳"

[project_types.Kubernetes]
indicators = ["*.yaml", "*.yml"]  # In k8s directories
icon = "☸️"
```

### Project-Specific Config (`.intermcli.toml`)

```toml
# Project-specific overrides

[scan-ports]
default_host = "dev.myproject.com"

# Custom ports for this project
[scan-ports.port_lists.project]
description = "Project-specific services"

[scan-ports.port_lists.project.ports]
"3001" = "API Server"
"3002" = "WebSocket Server"
"6000" = "Debug Port"
"8080" = "Admin Panel"

[find-projects]
# Only scan subdirectories in this project
development_dirs = ["./microservices", "./libs", "./tools"]
max_scan_depth = 2
```

## 🛠️ Environment Variables

Each tool supports environment variable overrides:

### Scan Ports
```bash
# Port scanner environment variables
export SCAN_PORTS_HOST=localhost
export SCAN_PORTS_TIMEOUT=5
export SCAN_PORTS_ENHANCED=true
```

### Find Projects
```bash
# Project finder environment variables
export FIND_PROJECTS_DIRS="~/Code:~/Work:~/Projects"
export FIND_PROJECTS_EDITOR="nvim"
export FIND_PROJECTS_DEPTH=4
```

## 📊 Configuration Precedence

Configuration values are resolved in the following order (highest to lowest priority):

1. **Command line arguments** - `--timeout 5`
2. **Environment variables** - `SCAN_PORTS_TIMEOUT=5`
3. **Project config** - `.intermcli.toml`
4. **User tool-specific** - `~/.config/intermcli/scan-ports.toml`
5. **User global** - `~/.config/intermcli/config.toml`
6. **Tool defaults** - `tools/scan-ports/config/defaults.toml`

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