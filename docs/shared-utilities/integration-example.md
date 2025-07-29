# Integration Example

This document provides a complete example of integrating all the shared utilities in a new IntermCLI tool. Use this as a reference when creating your own tools.

## Complete Tool Example

Below is a complete example of a tool that integrates all the shared utilities:

```python
#!/usr/bin/env python3
"""
example-tool: Demonstrate the integration of all IntermCLI shared utilities.

This tool serves as a reference implementation showing how to properly use
all the shared utilities in a consistent manner.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    example-tool data.json
    example-tool --verbose --timeout 5 data.json
    example-tool --check-deps
"""

import sys
from pathlib import Path

# Ensure shared utilities are available
parent_path = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, parent_path)
try:
    from shared.path_utils import require_shared_utilities
    require_shared_utilities()
except ImportError:
    # If even path_utils can't be imported, provide a fallback error
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

# Import shared utilities
from shared.config_loader import ConfigLoader
from shared.output import Output
from shared.enhancement_loader import EnhancementLoader
from shared.arg_parser import ArgumentParser
from shared.tool_metadata import ToolMetadata
from shared.network_utils import NetworkUtils

# Tool metadata
__version__ = "1.0.0"
TOOL_NAME = "example-tool"


# --- Core functionality ---
def process_input(input_file: str, config: dict, output: Output) -> dict:
    """
    Process input file according to configuration.

    Args:
        input_file: Path to input file
        config: Tool configuration
        output: Output utility for display

    Returns:
        dict: Processing results
    """
    # Start task
    output.task_start("Processing input", input_file)

    # Read input file
    try:
        with open(input_file, 'r') as f:
            content = f.read()

        # Process based on file type
        if input_file.endswith('.json'):
            import json
            data = json.loads(content)
        elif input_file.endswith('.txt'):
            data = {"content": content, "lines": len(content.splitlines())}
        else:
            data = {"content": content}

        # Apply network operations if requested
        if config.get("network", {}).get("enabled", False):
            output.subheader("Network Operations")
            network = NetworkUtils(timeout=config.get("network", {}).get("timeout", 3.0))

            # Process URLs in data
            if "url" in data:
                output.info(f"Fetching URL: {data['url']}")
                response = network.make_http_request(data["url"])
                data["http_response"] = response

        # Task complete
        output.task_complete("Processing input", f"Processed {input_file}")
        return data

    except Exception as e:
        output.error(f"Failed to process {input_file}: {str(e)}")
        return {"error": str(e)}


# --- Dependency checking ---
def check_dependencies():
    """Check status of optional dependencies"""
    enhancer = EnhancementLoader(TOOL_NAME)
    enhancer.check_dependency("rich", "Rich output formatting")
    enhancer.check_dependency("requests", "Enhanced HTTP support")
    enhancer.check_dependency("jsonschema", "JSON validation")

    # Register features
    enhancer.register_feature("enhanced_output", ["rich"])
    enhancer.register_feature("enhanced_http", ["requests"])
    enhancer.register_feature("json_validation", ["jsonschema"])

    # Print status
    enhancer.print_status()


# --- CLI ---
def main():
    """
    CLI entry point for example-tool.
    Demonstrates integration of all shared utilities.
    """
    # Initialize metadata
    metadata = ToolMetadata.for_current_tool(TOOL_NAME, __version__, sys.modules[__name__])

    # Use the shared ArgumentParser
    arg_parser = ArgumentParser(
        tool_name=TOOL_NAME,
        description=metadata.description,
        epilog=metadata.get_help_text(),
        version=__version__,
    )

    # Add common arguments
    arg_parser.add_common_arguments()
    arg_parser.add_output_arguments()

    # Add tool-specific arguments
    arg_parser.add_positional_argument("input_file", "Input file to process")
    arg_parser.add_option("timeout", "Network timeout in seconds",
                          short_name="t", type=float, default=3.0)
    arg_parser.add_flag("network", "Enable network operations", short_name="n")

    # Parse arguments
    args = arg_parser.parse_args_as_dict()

    # Check dependencies if requested
    if args.get("check_deps"):
        check_dependencies()
        return

    # Initialize output handling
    output = Output(TOOL_NAME, verbose=args.get("verbose", False))

    # Display banner with metadata
    output.banner(TOOL_NAME, __version__, {
        "Description": metadata.description,
    })

    # Load configuration
    config_loader = ConfigLoader(TOOL_NAME)

    # Add the tool's default configuration file
    default_config_path = Path(__file__).resolve().parent / "config" / "defaults.toml"
    if default_config_path.exists():
        config_loader.add_config_file(str(default_config_path))
    else:
        output.warning(f"Default config file not found at {default_config_path}")

    # Add custom config if specified
    if args.get("config"):
        config_loader.add_config_file(Path(args["config"]))

    # Load configuration with command line args
    config = config_loader.load_config(args)

    # Show config if requested
    if args.get("show_config"):
        output.header("Configuration")
        output.print_json(config)
        return

    # Process input
    if args.get("input_file"):
        output.header("Processing")

        # Set network config from args
        if "network" not in config:
            config["network"] = {}
        config["network"]["enabled"] = args.get("network", False)
        config["network"]["timeout"] = args.get("timeout", 3.0)

        # Process the input
        result = process_input(args["input_file"], config, output)

        # Show results
        output.header("Results")
        output.print_json(result)
    else:
        output.error("No input file provided")
        arg_parser.parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Utility Integration Points

The example demonstrates integration of all shared utilities:

1. **Path Utilities**: Used at the top of the file to ensure shared modules can be imported
2. **Tool Metadata**: Used to extract tool description and examples from docstring
3. **Argument Parser**: Used to parse command-line arguments with common patterns
4. **Config Loader**: Used to load configuration from files and command-line arguments
5. **Enhancement Loader**: Used to check for optional dependencies and features
6. **Output Handler**: Used for consistent output formatting
7. **Network Utilities**: Used for optional network operations

## Key Integration Patterns

### 1. Initial Setup

```python
# Ensure shared utilities are available
parent_path = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, parent_path)
try:
    from shared.path_utils import require_shared_utilities
    require_shared_utilities()
except ImportError:
    # Fallback error
    print("Error: IntermCLI shared utilities not found.")
    sys.exit(1)
```

### 2. Argument Parsing

```python
# Initialize metadata
metadata = ToolMetadata.for_current_tool(TOOL_NAME, __version__, sys.modules[__name__])

# Use the shared ArgumentParser
arg_parser = ArgumentParser(
    tool_name=TOOL_NAME,
    description=metadata.description,
    epilog=metadata.get_help_text(),
    version=__version__,
)

# Add common arguments
arg_parser.add_common_arguments()
```

### 3. Output Formatting

```python
# Initialize output handling
output = Output(TOOL_NAME, verbose=args.get("verbose", False))

# Display banner
output.banner(TOOL_NAME, __version__, {
    "Description": metadata.description,
})
```

### 4. Configuration Loading

```python
# Load configuration
config_loader = ConfigLoader(TOOL_NAME)
if args.get("config"):
    config_loader.add_config_file(Path(args["config"]))
config = config_loader.load_config(args)
```

### 5. Dependency Checking

```python
def check_dependencies():
    enhancer = EnhancementLoader(TOOL_NAME)
    enhancer.check_dependency("rich", "Rich output formatting")
    enhancer.register_feature("enhanced_output", ["rich"])
    enhancer.print_status()
```

## Best Practices

1. **Follow the established pattern** for tool structure
2. **Use all shared utilities** where appropriate
3. **Handle errors gracefully** with helpful messages
4. **Document your tool** with a clear docstring
5. **Support common arguments** like `--verbose` and `--config`
6. **Use progressive enhancement** for optional dependencies

## See Also

- [Developer Guide](../DEVELOPER-GUIDE.md) - Architecture, design principles, and contribution workflow
- All individual utility documentation in this directory
