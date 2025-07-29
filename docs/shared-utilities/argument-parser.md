# Argument Parser

The Argument Parser utility (`shared/arg_parser.py`) provides consistent argument parsing with common patterns across all IntermCLI tools. It extends Python's `argparse` module with pre-defined argument groups and common options.

## Key Features

- Consistent command-line interface across all tools
- Pre-defined common arguments (verbose, config, version, etc.)
- Support for argument grouping
- Simplified addition of positional and optional arguments
- Type conversion and validation

## Usage

### Basic Usage

```python
from shared.arg_parser import ArgumentParser

# Initialize with tool info
parser = ArgumentParser(
    tool_name="scan-ports",
    description="Scan ports on a remote host",
    version="1.0.0"
)

# Add tool-specific arguments
parser.parser.add_argument("target", help="Target host to scan")
parser.parser.add_argument("--port", "-p", type=int, help="Port to scan")

# Parse arguments
args = parser.parser.parse_args()

# Access arguments
target = args.target
port = args.port
```

### Adding Common Arguments

```python
from shared.arg_parser import ArgumentParser

# Initialize with tool info
parser = ArgumentParser(
    tool_name="scan-ports",
    description="Scan ports on a remote host",
    version="1.0.0"
)

# Add common arguments (--verbose, --help, --version)
parser.add_common_arguments()

# Add output arguments (--quiet, --json, --no-color)
parser.add_output_arguments()

# Parse arguments
args = parser.parser.parse_args()

# Check if verbose mode is enabled
if args.verbose:
    print("Verbose mode enabled")
```

### Simplified Argument Addition

```python
from shared.arg_parser import ArgumentParser

# Initialize with tool info
parser = ArgumentParser(
    tool_name="scan-ports",
    description="Scan ports on a remote host",
    version="1.0.0"
)

# Add positional argument
parser.add_positional_argument("target", "Target host to scan")

# Add option with short name
parser.add_option("port", "Port to scan", short_name="p", type=int)

# Add flag (boolean option)
parser.add_flag("verbose", "Enable verbose output", short_name="v")

# Parse arguments as dictionary
args = parser.parse_args_as_dict()

# Access arguments
target = args["target"]
port = args.get("port")  # Use get() for optional arguments
verbose = args.get("verbose", False)  # Provide default
```

### Argument Groups

```python
from shared.arg_parser import ArgumentParser

# Initialize with tool info
parser = ArgumentParser(
    tool_name="scan-ports",
    description="Scan ports on a remote host",
    version="1.0.0"
)

# Add argument groups
scan_group = parser.parser.add_argument_group("Scan Options")
output_group = parser.parser.add_argument_group("Output Options")

# Add arguments to groups
scan_group.add_argument("--timeout", type=float, default=1.0,
                        help="Timeout in seconds")
scan_group.add_argument("--parallel", action="store_true",
                        help="Scan ports in parallel")

output_group.add_argument("--json", action="store_true",
                          help="Output results as JSON")
output_group.add_argument("--quiet", action="store_true",
                          help="Suppress non-error output")

# Parse arguments
args = parser.parser.parse_args()
```

## Common Arguments

The ArgumentParser provides several pre-defined argument sets:

### Common Arguments

Added with `add_common_arguments()`:

- `--verbose`, `-v`: Enable verbose output
- `--help`, `-h`: Show help message and exit
- `--version`, `-V`: Show version information and exit
- `--config`: Path to config file
- `--check-deps`: Check optional dependency status

### Output Arguments

Added with `add_output_arguments()`:

- `--quiet`, `-q`: Suppress non-error output
- `--json`: Output results as JSON
- `--no-color`: Disable colored output

## Methods

| Method | Description |
|--------|-------------|
| `__init__(tool_name, description, epilog=None, version=None)` | Initialize argument parser |
| `add_common_arguments()` | Add common arguments (verbose, help, version, etc.) |
| `add_output_arguments()` | Add output-related arguments (quiet, json, no-color) |
| `add_positional_argument(name, help_text)` | Add a positional argument |
| `add_option(name, help_text, short_name=None, **kwargs)` | Add an optional argument |
| `add_flag(name, help_text, short_name=None)` | Add a boolean flag |
| `parse_args_as_dict()` | Parse arguments and return as dictionary |

## Best Practices

1. **Use consistent argument names** across all tools (e.g., `--verbose` not `--debug`)
2. **Provide short options** for commonly used arguments
3. **Group related arguments** for better help output
4. **Add the common arguments** to all tools
5. **Validate argument values** early in your tool's execution
6. **Provide meaningful help text** for all arguments

## See Also

- [Config Loader](config-loader.md) - For loading configuration from arguments
- [Tool Metadata](tool-metadata.md) - For consistent tool metadata handling
