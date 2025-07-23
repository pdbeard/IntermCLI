# Shared Utilities

IntermCLI provides a set of shared utilities that can be used across all tools in the suite. These utilities help maintain consistency, reduce code duplication, and make the codebase more maintainable.

**Note:** Detailed documentation for each utility has been moved to the [shared-utilities](./shared-utilities/index.md) directory.

## Available Utilities

| Utility | Description | File |
|---------|-------------|------|
| [Config Loader](./shared-utilities/config-loader.md) | Handles TOML configuration loading with proper precedence | `shared/config_loader.py` |
| [Enhancement Loader](./shared-utilities/enhancement-loader.md) | Handles detection of optional dependencies | `shared/enhancement_loader.py` |
| [Output Handler](./shared-utilities/output-handler.md) | Provides consistent output formatting | `shared/output.py` |
| [Error Handler](./shared-utilities/error-handler.md) | Provides standardized error handling | `shared/error_handler.py` |
| [Network Utilities](./shared-utilities/network-utils.md) | Provides common network operations | `shared/network_utils.py` |
| [Argument Parser](./shared-utilities/argument-parser.md) | Provides consistent argument parsing | `shared/arg_parser.py` |
| [Path Utilities](./shared-utilities/path-utils.md) | Ensures shared modules can be imported properly | `shared/path_utils.py` |
| [Tool Metadata](./shared-utilities/tool-metadata.md) | Provides consistent version and documentation handling | `shared/tool_metadata.py` |

## Integration Example

For a complete example of using all shared utilities together, see the [Integration Example](./shared-utilities/integration-example.md).

## See Also

- [Output Style Guide](./output-style-guide.md) - Guidelines for consistent output formatting
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Guidelines for contributing to IntermCLI
enhancements.register_feature("enhanced_http", ["requests"])
enhancements.register_feature("rich_output", ["rich"])

# Get missing dependencies
missing_deps = enhancements.get_missing_dependencies()

# Print status
enhancements.print_status()
```

### Output Handler (`shared/output.py`)

Provides consistent output formatting with optional rich enhancements. For comprehensive output styling guidelines, see [Output Style Guide](/docs/output-style-guide.md).

**Example Usage:**

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Tool banner and configuration display
output.banner("scan-ports", "1.0.0", {
    "Target": "example.com",
    "Ports": "1-1000",
    "Timeout": "2s"
})

# Section headers
output.header("Scan Results")
output.subheader("Open Ports")

# Task start/completion
output.task_start("Scanning ports")
# ... do work ...
output.task_complete("Scanning ports", "Found 3 open ports")

# Print different types of messages
output.info("Regular information")
output.success("Operation completed successfully")
output.warning("Something might be wrong")
output.error("Something went wrong")

# Key-value pairs
output.item("Host", "example.com")
output.item("Total ports", "1000")
output.item("Open ports", "3")

# Print tables
headers = ["Port", "State", "Service"]
rows = [
    ["22", "open", "SSH"],
    ["80", "open", "HTTP"],
    ["443", "open", "HTTPS"]
]
output.print_table(headers, rows)

# Create progress bars
with output.create_progress_bar(total=100, description="Scanning") as progress:
    for i in range(100):
        # Do some work
        progress.update(1)
```

### Network Utilities (`shared/network_utils.py`)

Provides common network operations with optional enhanced functionality.

**Example Usage:**

```python
from shared.network_utils import NetworkUtils

# Initialize with timeout
network = NetworkUtils(timeout=3.0)

# Check if a port is open
is_open = network.check_port("localhost", 8080)

# Scan multiple ports
open_ports = network.scan_ports("example.com", [80, 443, 8080])

# Detect service on a port
banner = network.detect_service_banner("localhost", 22)

# Make HTTP requests (with fallback between requests and urllib)
response = network.make_http_request("https://api.example.com/data")
```

### Argument Parser (`shared/arg_parser.py`)

Provides consistent argument parsing with common patterns.

**Example Usage:**

```python
from shared.arg_parser import ArgumentParser

# Initialize with tool info
parser = ArgumentParser(
    tool_name="scan-ports",
    description="Scan ports on a remote host",
    version="1.0.0"
)

# Add common arguments
parser.add_common_arguments()
parser.add_output_arguments()

# Add tool-specific arguments
parser.add_option("port", "Port to scan", short_name="p", type=int)
parser.add_flag("verbose", "Enable verbose output", short_name="v")

# Parse arguments
args = parser.parse_args_as_dict()
```

## Using Shared Utilities in New Tools

When creating a new tool for the IntermCLI suite, you should use these shared utilities to maintain consistency. Here's an example of how to structure a new tool:

```python
#!/usr/bin/env python3
"""
my-tool: Brief description of what the tool does.
Longer description with more details.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    my-tool example
    my-tool --option value
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from shared.arg_parser import ArgumentParser
from shared.config_loader import ConfigLoader
from shared.enhancement_loader import EnhancementLoader
from shared.output import Output
from shared.network_utils import NetworkUtils

__version__ = "1.0.0"


def main():
    # Parse arguments
    parser = ArgumentParser(
        tool_name="my-tool",
        description="Brief description of what the tool does",
        version=__version__
    )
    parser.add_common_arguments()
    parser.add_output_arguments()

    # Add tool-specific arguments
    parser.add_positional_argument("target", "Target to process")

    # Parse arguments
    args = parser.parse_args_as_dict()

    # Check dependencies
    enhancements = EnhancementLoader("my-tool")
    enhancements.check_dependency("requests")
    enhancements.check_dependency("rich")

    # Register features
    enhancements.register_feature("enhanced_output", ["rich"])

    # Check if we should just show dependencies and exit
    if args.get("check_deps"):
        enhancements.print_status()
        sys.exit(0)

    # Initialize output
    output = Output(
        "my-tool",
        use_rich=enhancements.dependencies.get("rich", False),
        verbose=args.get("verbose", False)
    )

    # Load configuration
    config_loader = ConfigLoader("my-tool")
    config = config_loader.load_config(args)

    # Show configuration if requested
    if args.get("show_config"):
        output.info(f"Configuration loaded from: {config_loader.config_source}")
        output.print_json(config, "Current Configuration")
        sys.exit(0)

    # Main tool logic
    output.info(f"Processing {args['target']}")

    # Example of using network utilities
    if enhancements.dependencies.get("requests"):
        network = NetworkUtils()
        result = network.make_http_request(f"https://{args['target']}")
        output.print_json(result, "HTTP Response")

    output.success("Operation completed successfully")


if __name__ == "__main__":
    main()
```
