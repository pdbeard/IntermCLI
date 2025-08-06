# Shared Utilities Reference

IntermCLI includes a comprehensive set of shared utilities that provide consistent functionality across all tools. This reference guide contains everything you need to know about using these utilities in your tool development.

## Configuration System (`config_loader.py`)

The configuration system provides hierarchical configuration loading with fallbacks:

1. Command line arguments
2. Environment variables
3. Project-specific configuration
4. User configuration
5. Tool defaults

debug_mode = settings.get("debug", False)
```python
from shared.config_loader import ConfigLoader

# Initialize with tool name
config_loader = ConfigLoader("my-tool")

# Load configuration with fallbacks
settings = config_loader.load_config()

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
from shared.arg_parser import ArgumentParser

# Create a parser with tool metadata
parser = ArgumentParser(
    tool_name="my-tool",
    description="My amazing tool description",
    version="1.0.0"
)

# Add tool-specific arguments
parser.parser.add_argument("--option", help="Tool-specific option")

# Parse arguments
args = parser.parser.parse_args()
```

### Key Features:
- Consistent help text formatting
- Built-in version handling
- Integration with config system
- Common argument patterns

## Output Handler (`output.py`)

The output handler ensures consistent terminal output formatting across all tools:

```python
from shared.output import Output

# Initialize output handler
output = Output("my-tool")

# Display various message types
output.header("Operation Starting")
output.info("Processing file: example.txt")
output.warning("Resource usage is high")
output.success("Operation completed successfully")
output.error("Failed to connect to service")
```

### Key Features:
- Consistent color schemes
- Level-based formatting
- Support for rich text when available
- Quiet mode support

## Error Handler (`error_handler.py`)

The error handler provides standardized error handling and reporting:

```python
from shared.output import Output
from shared.error_handler import ErrorHandler

output = Output("my-tool")
error_handler = ErrorHandler(output)

try:
    # Your code here
    result = potentially_failing_function()
except Exception as e:
    msg, code = error_handler.handle_file_operation("somefile.txt", e)
    output.error(msg)
    # Optionally exit or handle further
```

### Key Features:
- Standardized error formatting
- Multiple error levels (INFO, WARNING, ERROR, FATAL)
- Debug mode support
- Exit code handling

## Enhancement Loader (`enhancement_loader.py`)

The enhancement loader enables graceful handling of optional dependencies:

```python
from shared.enhancement_loader import EnhancementLoader

enhancements = EnhancementLoader("my-tool")
has_rich = enhancements.check_dependency("rich")

if has_rich:
    import rich
    rich.print("[bold green]Enhanced output enabled[/bold green]")
else:
    print("Enhanced output disabled (install 'rich' package to enable)")
```

### Key Features:
- Graceful fallbacks for missing dependencies
- User-friendly installation suggestions
- No hard dependencies on optional packages

## Network Utilities (`network_utils.py`)
download_file("https://example.com/file.zip", "file.zip")

The network utilities module provides common network operations:

```python
from shared.network_utils import NetworkUtils

network = NetworkUtils(timeout=3.0)

# Check if port is open
is_open = network.check_port("example.com", 80)

# Scan multiple ports
open_ports = network.scan_ports("example.com", [80, 443, 8080])

# Detect service on a port
banner = network.detect_service_banner("localhost", 22)

# Make HTTP request (with fallback between requests and urllib)
response = network.make_http_request("https://api.example.com/data")
```

### Key Features:
- Consistent error handling
- Progress reporting
- Timeout management
- Proxy support

## Path Utilities (`path_utils.py`)
data_dir = ensure_dir_exists(f"{root}/data")
temp_dir = get_temp_dir()

The path utilities ensure consistent path handling across platforms:

```python
from shared.path_utils import add_shared_path, ensure_shared_imports, require_shared_utilities

# Add the shared module directory to the Python path
add_shared_path()

# Ensure shared modules can be imported
if ensure_shared_imports():
    print("Shared utilities are available.")
else:
    print("Shared utilities are missing.")

# Require shared utilities or exit
require_shared_utilities()
```

### Key Features:
- Cross-platform path normalization
- Common directory helpers
- Directory creation with permissions

## Tool Metadata (`tool_metadata.py`)
description = get_tool_description()

The tool metadata module provides consistent version and documentation handling:

```python
from shared.tool_metadata import ToolMetadata

metadata = ToolMetadata(
    tool_name="my-tool",
    version="1.0.0",
    description="My tool description",
    examples=["my-tool --help", "my-tool run"]
)

print(metadata.get_full_name())
print(metadata.get_banner())
print(metadata.get_help_text())
```

### Key Features:
- Centralized version management
- Documentation integration
- Tool manifest handling

## Integration Example

Here's a complete example showing how these utilities work together:

```python
#!/usr/bin/env python3

from shared.arg_parser import ArgumentParser
from shared.config_loader import ConfigLoader
from shared.output import Output
from shared.error_handler import ErrorHandler
from shared.tool_metadata import ToolMetadata

def main():
    tool_name = "example-tool"
    metadata = ToolMetadata(
        tool_name=tool_name,
        version="1.0.0",
        description="Example tool for IntermCLI"
    )

    # Create parser with metadata
    parser = ArgumentParser(
        tool_name=tool_name,
        description=metadata.description,
        version=metadata.version
    )
    parser.parser.add_argument("--option", help="Tool-specific option")
    args = parser.parser.parse_args()

    # Load configuration with fallbacks
    config_loader = ConfigLoader(tool_name)
    settings = config_loader.load_config()

    # Merge arguments with configuration
    option_value = getattr(args, "option", None) or settings.get("option")

    output = Output(tool_name)
    error_handler = ErrorHandler(output)

    try:
        output.header(f"Starting {tool_name}")
        # Tool-specific logic here
        # ...
        output.success(f"{tool_name} completed successfully")
        return 0
    except Exception as e:
        msg, code = error_handler.handle_file_operation("somefile.txt", e)
        output.error(msg)
        return 1

if __name__ == "__main__":
    exit(main())
```

This document provides a comprehensive reference for all shared utilities available in IntermCLI. By using these consistent components, tools maintain a unified experience while reducing code duplication and improving maintainability.
