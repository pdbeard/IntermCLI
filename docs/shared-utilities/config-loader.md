# Config Loader

The Config Loader utility (`shared/config_loader.py`) handles TOML configuration loading with proper precedence, ensuring that configuration is loaded consistently across all IntermCLI tools.

## Configuration Precedence

The Config Loader follows this precedence order when loading configuration:

1. Command line arguments
2. Environment variables
3. Project-level config (`.intermcli.toml`)
4. User tool-specific config (`~/.config/intermcli/{tool}.toml`)
5. User global config (`~/.config/intermcli/config.toml`)
6. Tool default config (`tools/{tool}/config/defaults.toml`)
7. Built-in defaults

This ensures that user-specific configurations can override defaults, and command-line arguments always take precedence.

## Usage

### Basic Usage

```python
from shared.config_loader import ConfigLoader

# Initialize with tool name
config_loader = ConfigLoader("scan-ports")

# Load configuration
config = config_loader.load_config()

# Access configuration values
timeout = config.get("timeout", 30)
```

### Adding Custom Config Files

```python
from pathlib import Path
from shared.config_loader import ConfigLoader

# Initialize with tool name
config_loader = ConfigLoader("scan-ports")

# Add a custom config file (will be loaded with highest precedence)
config_loader.add_config_file(Path("/path/to/custom/config.toml"))

# Load configuration
config = config_loader.load_config()
```

### With Command Line Arguments

```python
from shared.config_loader import ConfigLoader
from shared.arg_parser import ArgumentParser

# Parse arguments
parser = ArgumentParser("scan-ports")
parser.add_common_arguments()
args = parser.parse_args_as_dict()

# Initialize with tool name
config_loader = ConfigLoader("scan-ports")

# Load configuration with command line arguments
config = config_loader.load_config(args)
```

### Accessing Nested Configuration

```python
from shared.config_loader import ConfigLoader

# Initialize with tool name
config_loader = ConfigLoader("scan-ports")

# Load configuration
config = config_loader.load_config()

# Access nested configuration with dot notation
timeout = config_loader.get("network.timeout", 30)
```

## Methods

| Method | Description |
|--------|-------------|
| `__init__(tool_name, auto_load=True)` | Initialize the config loader for a specific tool |
| `add_config_file(file_path)` | Add a custom config file to be loaded |
| `load_config(args=None)` | Load configuration from all sources |
| `get(key, default=None)` | Get a configuration value (supports dot notation) |
| `set(key, value)` | Set a configuration value (supports dot notation) |

## Default Config Structure

Each tool should have a default configuration file at `tools/{tool}/config/defaults.toml`. This file should contain all default configuration values for the tool.

Example default config structure:

```toml
# Default configuration for scan-ports

# Network settings
[network]
timeout = 3.0
retries = 3
parallel = true

# Output settings
[output]
verbose = false
json = false
```

## Environment Variables

Environment variables are also supported for configuration. The environment variable names should follow this pattern:

```
INTERMCLI_{TOOL}_{KEY}
```

For example, to set the network timeout for the `scan-ports` tool:

```
INTERMCLI_SCAN_PORTS_NETWORK_TIMEOUT=5.0
```

## See Also

- [Argument Parser](argument-parser.md) - For handling command line arguments
- [Tool Metadata](tool-metadata.md) - For handling tool metadata
