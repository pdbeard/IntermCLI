# ⚙️ IntermCLI Configuration

## Overview

IntermCLI uses a hierarchical configuration system that allows for flexible customization at multiple levels. Configuration files use JSON format for simplicity and cross-platform compatibility.

## 📁 Configuration File Locations

Configuration files are loaded in the following priority order (later files override earlier ones):

1. **System Defaults** - `config/defaults.json` (in repository)
2. **User Global Config** - `~/.config/intermcli/config.json`
3. **Project Local Config** - `.intermcli.json` (in current directory)
4. **Command Line Arguments** - Override any config value

### Configuration Directory Structure

```
~/.config/intermcli/
├── config.json          # Main user configuration
├── ports.json           # Custom port definitions
├── projects.json        # Project discovery settings
├── plugins/             # User plugins directory
└── cache/              # Cached data
```

## 🔧 Core Configuration

### Default Configuration (`config/defaults.json`)

```json
{
  "version": "1.0.0",
  "general": {
    "default_timeout": 3,
    "max_threads": 50,
    "output_format": "auto",
    "interactive_mode": true,
    "show_progress": true,
    "color_output": true,
    "emoji_output": true
  },
  "scanner": {
    "default_host": "localhost",
    "service_detection": true,
    "enhanced_detection": "auto",
    "show_closed_ports": false,
    "confidence_threshold": "medium",
    "scan_delay": 0,
    "retry_attempts": 1
  },
  "finder": {
    "search_paths": [
      "~/Development",
      "~/Projects",
      "~/Code",
      "~/workspace"
    ],
    "max_depth": 3,
    "follow_symlinks": false,
    "ignore_patterns": [
      ".git",
      "node_modules",
      "__pycache__",
      ".venv",
      ".env"
    ],
    "project_indicators": [
      ".git",
      "package.json",
      "requirements.txt",
      "Cargo.toml",
      "go.mod",
      "pom.xml"
    ]
  },
  "output": {
    "verbosity": "normal",
    "timestamp": false,
    "save_results": false,
    "results_dir": "~/.local/share/intermcli/results"
  },
  "ui": {
    "confirm_external_scans": true,
    "confirm_destructive_actions": true,
    "auto_open_editor": false,
    "preferred_editor": "auto"
  }
}
```

## 🔍 Port Scanner Configuration

### Port Definitions (`config/ports.json`)

```json
{
  "version": "1.0.0",
  "port_lists": {
    "common": {
      "description": "Most commonly used ports",
      "ports": {
        "22": "SSH",
        "23": "Telnet",
        "25": "SMTP",
        "53": "DNS",
        "80": "HTTP",
        "110": "POP3",
        "143": "IMAP",
        "443": "HTTPS",
        "993": "IMAPS",
        "995": "POP3S"
      }
    },
    "web": {
      "description": "Web development and HTTP services",
      "ports": {
        "80": "HTTP",
        "443": "HTTPS",
        "3000": "Node.js Dev Server",
        "3001": "React Dev Server",
        "4000": "Ruby/Rails Dev",
        "5000": "Flask/Python Dev",
        "8000": "Django Dev/HTTP Alt",
        "8080": "HTTP Proxy/Alt",
        "8443": "HTTPS Alt",
        "9000": "Various Dev Servers"
      }
    },
    "database": {
      "description": "Database services",
      "ports": {
        "1433": "SQL Server",
        "3306": "MySQL/MariaDB",
        "5432": "PostgreSQL",
        "6379": "Redis",
        "9200": "Elasticsearch",
        "27017": "MongoDB",
        "5984": "CouchDB",
        "8086": "InfluxDB"
      }
    },
    "docker": {
      "description": "Docker and container services",
      "ports": {
        "2375": "Docker Daemon (HTTP)",
        "2376": "Docker Daemon (HTTPS)",
        "2377": "Docker Swarm",
        "4789": "Docker Overlay Network",
        "7946": "Docker Swarm Network",
        "9000": "Portainer",
        "19000": "Docker Registry"
      }
    },
    "messaging": {
      "description": "Message queues and communication",
      "ports": {
        "1883": "MQTT",
        "4369": "Erlang Port Mapper",
        "5671": "AMQP (TLS)",
        "5672": "AMQP/RabbitMQ",
        "6667": "IRC",
        "9092": "Kafka",
        "15672": "RabbitMQ Management"
      }
    },
    "security": {
      "description": "Security and monitoring tools",
      "ports": {
        "161": "SNMP",
        "389": "LDAP",
        "636": "LDAPS",
        "1812": "RADIUS",
        "8200": "HashiCorp Vault",
        "9090": "Prometheus",
        "3000": "Grafana",
        "5601": "Kibana"
      }
    }
  },
  "service_detection": {
    "http_user_agent": "intermcli/1.0.0",
    "connection_timeout": 5,
    "read_timeout": 3,
    "ssl_verify": false,
    "follow_redirects": true,
    "max_redirects": 3,
    "detect_frameworks": true,
    "extract_versions": true
  }
}
```

## 📁 Project Finder Configuration

### Project Discovery Settings

```json
{
  "finder": {
    "search_paths": [
      "~/Development",
      "~/Projects", 
      "~/Code",
      "~/workspace",
      "~/src"
    ],
    "exclude_paths": [
      "~/Development/archive",
      "~/Development/temp"
    ],
    "max_depth": 3,
    "follow_symlinks": false,
    "scan_hidden_dirs": false,
    "project_types": {
      "git": {
        "indicators": [".git"],
        "priority": 10,
        "icon": "📁"
      },
      "node": {
        "indicators": ["package.json"],
        "priority": 9,
        "icon": "📦"
      },
      "python": {
        "indicators": ["requirements.txt", "setup.py", "pyproject.toml"],
        "priority": 8,
        "icon": "🐍"
      },
      "rust": {
        "indicators": ["Cargo.toml"],
        "priority": 8,
        "icon": "🦀"
      },
      "go": {
        "indicators": ["go.mod", "go.sum"],
        "priority": 8,
        "icon": "🐹"
      },
      "java": {
        "indicators": ["pom.xml", "build.gradle"],
        "priority": 7,
        "icon": "☕"
      },
      "docker": {
        "indicators": ["Dockerfile", "docker-compose.yml"],
        "priority": 6,
        "icon": "🐳"
      }
    },
    "ignore_patterns": [
      ".git",
      "node_modules",
      "__pycache__",
      ".venv",
      "venv",
      ".env",
      "target",
      "build",
      "dist",
      ".next",
      ".nuxt"
    ],
    "cache_results": true,
    "cache_duration": 3600,
    "auto_refresh": true
  },
  "editor_integration": {
    "preferred_editor": "auto",
    "editor_commands": {
      "vscode": "code",
      "vim": "vim",
      "nvim": "nvim",
      "emacs": "emacs",
      "sublime": "subl",
      "atom": "atom"
    },
    "auto_detect_editor": true,
    "open_in_background": false
  }
}
```

## 🎨 Output and UI Configuration

### Display Settings

```json
{
  "output": {
    "format": "auto",
    "color_scheme": "auto",
    "emoji_support": true,
    "unicode_support": true,
    "table_style": "rounded",
    "show_timestamps": false,
    "show_duration": true,
    "verbosity": "normal",
    "log_level": "info"
  },
  "ui": {
    "interactive_mode": true,
    "confirm_actions": {
      "external_scans": true,
      "destructive_operations": true,
      "large_operations": true
    },
    "progress_indicators": {
      "show_progress_bars": true,
      "show_spinners": true,
      "show_counters": true,
      "update_interval": 0.1
    },
    "keyboard_shortcuts": {
      "quit": ["q", "ctrl+c"],
      "help": ["h", "?"],
      "refresh": ["r", "f5"],
      "toggle_details": ["d"],
      "filter": ["/"]
    }
  }
}
```

## 🔧 User Configuration Examples

### Basic User Config (`~/.config/intermcli/config.json`)

```json
{
  "general": {
    "default_timeout": 5,
    "output_format": "rich",
    "interactive_mode": true
  },
  "scanner": {
    "enhanced_detection": true,
    "show_closed_ports": false,
    "default_host": "localhost"
  },
  "finder": {
    "search_paths": [
      "~/Code",
      "~/Projects",
      "~/Work"
    ],
    "max_depth": 4,
    "auto_refresh": true
  },
  "ui": {
    "preferred_editor": "code",
    "auto_open_editor": true,
    "confirm_external_scans": true
  }
}
```

### Advanced User Config

```json
{
  "general": {
    "max_threads": 100,
    "default_timeout": 2,
    "output_format": "json"
  },
  "scanner": {
    "service_detection": true,
    "enhanced_detection": true,
    "confidence_threshold": "high",
    "scan_delay": 0.1,
    "retry_attempts": 3,
    "custom_ports": {
      "development": {
        "3000": "React Dev",
        "3001": "Next.js",
        "4000": "Vue Dev",
        "5000": "Flask",
        "8080": "Spring Boot"
      }
    }
  },
  "finder": {
    "search_paths": [
      "~/Development",
      "~/opensource",
      "/workspace"
    ],
    "exclude_paths": [
      "~/Development/archived"
    ],
    "max_depth": 5,
    "follow_symlinks": true,
    "custom_project_types": {
      "terraform": {
        "indicators": ["*.tf", "terraform.tfvars"],
        "priority": 7,
        "icon": "🏗️"
      }
    }
  },
  "output": {
    "save_results": true,
    "results_format": "json",
    "results_dir": "~/logs/intermcli"
  }
}
```

### Project-Specific Config (`.intermcli.json`)

```json
{
  "scanner": {
    "default_host": "dev.myproject.com",
    "port_lists": ["web", "database"],
    "custom_ports": {
      "project_specific": {
        "3001": "API Server",
        "3002": "WebSocket Server",
        "6000": "Debug Port"
      }
    }
  },
  "finder": {
    "search_paths": ["./microservices", "./libs"],
    "max_depth": 2
  }
}
```

## 🛠️ Configuration Commands

### View Configuration

```bash
# Show current effective configuration
interm config show

# Show specific section
interm config show scanner
interm config show finder

# Show configuration sources
interm config sources

# Validate configuration
interm config validate
```

### Modify Configuration

```bash
# Set configuration value
interm config set general.default_timeout 5
interm config set scanner.enhanced_detection true

# Add to list
interm config add finder.search_paths ~/NewProjects

# Remove from list  
interm config remove finder.search_paths ~/OldProjects

# Reset to defaults
interm config reset
interm config reset scanner
```

### Configuration Wizard

```bash
# Interactive configuration setup
interm config init

# Guided setup for specific features
interm config setup scanner
interm config setup finder
```

## 📋 Configuration Validation

### Schema Validation

IntermCLI validates configuration files against a JSON schema to ensure correctness:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "general": {
      "type": "object",
      "properties": {
        "default_timeout": {
          "type": "number",
          "minimum": 0.1,
          "maximum": 300
        },
        "max_threads": {
          "type": "integer",
          "minimum": 1,
          "maximum": 1000
        }
      }
    }
  },
  "required": ["version"]
}
```

### Common Validation Errors

| Error | Description | Solution |
|-------|-------------|----------|
| Invalid timeout | Timeout value out of range | Set between 0.1 and 300 seconds |
| Invalid path | Path doesn't exist | Use absolute path or `~` for home |
| Invalid port | Port number out of range | Use ports 1-65535 |
| Invalid format | JSON syntax error | Check JSON formatting |
| Missing required | Required field missing | Add required configuration fields |

## 🔍 Environment Variables

Configuration can also be set via environment variables:

```bash
# General settings
export INTERM_TIMEOUT=5
export INTERM_THREADS=100
export INTERM_OUTPUT_FORMAT=json

# Scanner settings
export INTERM_SCANNER_HOST=localhost
export INTERM_SCANNER_ENHANCED=true

# Finder settings
export INTERM_FINDER_PATHS=~/Code:~/Projects
export INTERM_FINDER_DEPTH=3

# UI settings
export INTERM_EDITOR=code
export INTERM_INTERACTIVE=true
```

Environment variables follow the pattern: `INTERM_<SECTION>_<KEY>=<VALUE>`

## 📊 Configuration Precedence

Configuration values are resolved in the following order (highest to lowest priority):

1. **Command line arguments** - `--timeout 5`
2. **Environment variables** - `INTERM_TIMEOUT=5`
3. **Project config** - `.intermcli.json`
4. **User config** - `~/.config/intermcli/config.json`
5. **System defaults** - `config/defaults.json`

## 🚀 Performance Configuration

### Optimization Settings

```json
{
  "performance": {
    "scanner": {
      "connection_pool_size": 50,
      "dns_cache_ttl": 300,
      "keep_alive": true,
      "batch_size": 100
    },
    "finder": {
      "fs_cache_size": 1000,
      "parallel_scan": true,
      "memory_limit": "100MB"
    },
    "output": {
      "buffer_size": 8192,
      "flush_interval": 1.0
    }
  }
}
```

## 🔐 Security Configuration

### Security Settings

```json
{
  "security": {
    "scanner": {
      "rate_limit": {
        "enabled": true,
        "max_requests_per_second": 100,
        "burst_size": 200
      },
      "allowed_hosts": ["*"],
      "blocked_hosts": [],
      "respect_robots_txt": false
    },
    "finder": {
      "respect_gitignore": true,
      "follow_symlinks": false,
      "max_file_size": "10MB"
    },
    "general": {
      "log_sensitive_data": false,
      "secure_temp_files": true
    }
  }
}
```

## 🔧 Troubleshooting Configuration

### Common Issues

1. **Configuration not loading**
   ```bash
   # Check file permissions
   ls -la ~/.config/intermcli/config.json
   
   # Validate JSON syntax
   interm config validate
   ```

2. **Settings not taking effect**
   ```bash
   # Check configuration precedence
   interm config sources
   
   # Show effective configuration
   interm config show
   ```

3. **Performance issues**
   ```bash
   # Check thread and timeout settings
   interm config show general.max_threads
   interm config show general.default_timeout
   ```

### Debug Mode

```bash
# Enable debug output
interm --debug config show
interm --debug scan localhost

# Verbose configuration loading
interm --verbose config validate
```

---

This configuration system provides flexibility while maintaining sensible defaults, allowing users to customize IntermCLI to their specific needs and workflows.