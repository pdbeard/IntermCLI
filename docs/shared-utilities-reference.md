# Shared Utilities Reference

IntermCLI includes a comprehensive set of shared utilities that provide consistent functionality across all tools. This reference guide contains everything you need to know about using these utilities in your tool development.

## Configuration System (`config_loader.py`)

The configuration system provides hierarchical configuration loading with fallbacks:

1. Command line arguments
2. Environment variables
3. Project-specific configuration
4. User configuration
5. Tool defaults

```python
from shared.config_loader import ConfigManager

# Initialize with tool name
config = ConfigManager("my-tool")

# Load configuration with fallbacks
settings = config.load_config()

# Access configuration values
debug_mode = settings.get("debug", False)
```

### Key Features:
- TOML-based configuration
- Hierarchical fallback system
- Environment variable support (prefixed with `INTERMCLI_`)
- Automatic schema validation

## Argument Parser (`arg_parser.py`)

The argument parser provides consistent command-line argument handling for all tools:

```python
from shared.arg_parser import create_parser

# Create a parser with tool metadata
parser = create_parser(
    name="my-tool",
    description="My amazing tool description",
    version="1.0.0"
)

# Add tool-specific arguments
parser.add_argument("--option", help="Tool-specific option")

# Parse arguments
args = parser.parse_args()
```

### Key Features:
- Consistent help text formatting
- Built-in version handling
- Integration with config system
- Common argument patterns

## Output Handler (`output.py`)

The output handler ensures consistent terminal output formatting across all tools:

```python
from shared.output import print_header, print_success, print_info, print_warning, print_error

# Display various message types
print_header("Operation Starting")
print_info("Processing file: example.txt")
print_warning("Resource usage is high")
print_success("Operation completed successfully")
print_error("Failed to connect to service")
```

### Key Features:
- Consistent color schemes
- Level-based formatting
- Support for rich text when available
- Quiet mode support

## Error Handler (`error_handler.py`)

The error handler provides standardized error handling and reporting:

```python
from shared.error_handler import handle_error, ErrorLevel

try:
    # Your code here
    result = potentially_failing_function()
except Exception as e:
    # Handle with appropriate error level
    handle_error(e, ErrorLevel.WARNING)
    # Or exit with error
    handle_error(e, ErrorLevel.FATAL, exit_code=1)
```

### Key Features:
- Standardized error formatting
- Multiple error levels (INFO, WARNING, ERROR, FATAL)
- Debug mode support
- Exit code handling

## Enhancement Loader (`enhancement_loader.py`)

The enhancement loader enables graceful handling of optional dependencies:

```python
from shared.enhancement_loader import try_import

# Try to import an optional dependency
rich = try_import("rich", "For enhanced terminal output")

# Use if available, fallback if not
if rich:
    rich.print("[bold green]Enhanced output enabled[/bold green]")
else:
    print("Enhanced output disabled (install 'rich' package to enable)")
```

### Key Features:
- Graceful fallbacks for missing dependencies
- User-friendly installation suggestions
- No hard dependencies on optional packages

## Network Utilities (`network_utils.py`)

The network utilities module provides common network operations:

```python
from shared.network_utils import (
    check_port_open, get_local_ip, download_file, make_request
)

# Check if port is open
is_open = check_port_open("example.com", 80)

# Get local IP address
local_ip = get_local_ip()

# Download a file with progress
download_file("https://example.com/file.zip", "file.zip")

# Make HTTP request with error handling
response = make_request("https://api.example.com/data")
```

### Key Features:
- Consistent error handling
- Progress reporting
- Timeout management
- Proxy support

## Path Utilities (`path_utils.py`)

The path utilities ensure consistent path handling across platforms:

```python
from shared.path_utils import (
    get_project_root, ensure_dir_exists, normalize_path,
    get_config_dir, get_temp_dir
)

# Get project root directory
root = get_project_root()

# Ensure directory exists
data_dir = ensure_dir_exists(f"{root}/data")

# Normalize path across platforms
path = normalize_path("~/documents/file.txt")

# Get configuration directory
config_dir = get_config_dir()

# Get temporary directory
temp_dir = get_temp_dir()
```

### Key Features:
- Cross-platform path normalization
- Common directory helpers
- Directory creation with permissions

## Tool Metadata (`tool_metadata.py`)

The tool metadata module provides consistent version and documentation handling:

```python
from shared.tool_metadata import (
    get_tool_version, get_tool_description,
    get_tool_manifest, load_manifest
)

# Get version of current tool
version = get_tool_version()

# Get tool description
description = get_tool_description()

# Get tool manifest data
manifest = get_tool_manifest("my-tool")

# Load the entire tools manifest
all_tools = load_manifest()
```

### Key Features:
- Centralized version management
- Documentation integration
- Tool manifest handling

## Integration Example

Here's a complete example showing how these utilities work together:

```python
#!/usr/bin/env python3

from shared.arg_parser import create_parser
from shared.config_loader import ConfigManager
from shared.output import print_header, print_success, print_error
from shared.error_handler import handle_error, ErrorLevel
from shared.tool_metadata import get_tool_version, get_tool_description

def main():
    # Set up tool with consistent metadata
    tool_name = "example-tool"

    # Create parser with metadata
    parser = create_parser(
        name=tool_name,
        description=get_tool_description(tool_name),
        version=get_tool_version(tool_name)
    )

    # Add tool-specific arguments
    parser.add_argument("--option", help="Tool-specific option")

    # Parse arguments
    args = parser.parse_args()

    # Load configuration with fallbacks
    config = ConfigManager(tool_name)
    settings = config.load_config()

    # Merge arguments with configuration
    option_value = args.option or settings.get("option")

    try:
        # Tool operation begins
        print_header(f"Starting {tool_name}")

        # Tool-specific logic here
        # ...

        # Success message
        print_success(f"{tool_name} completed successfully")
        return 0

    except Exception as e:
        # Handle error and exit
        handle_error(e, ErrorLevel.FATAL, exit_code=1)
        return 1

if __name__ == "__main__":
    exit(main())
```

This document provides a comprehensive reference for all shared utilities available in IntermCLI. By using these consistent components, tools maintain a unified experience while reducing code duplication and improving maintainability.
