#!/usr/bin/env python3
"""
template-tool: Brief description of what this tool does in one sentence.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    template-tool [args]
    template-tool --option value
    template-tool --copy source destination
    template-tool --recursive directory
    template-tool --dry-run --verbose
"""

import sys
import time
from pathlib import Path

# Ensure shared utilities are available
parent_path = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, parent_path)
try:
    from shared.path_utils import require_shared_utilities

    require_shared_utilities()

    # Import shared utilities after path setup
    from shared.arg_parser import ArgumentParser
    from shared.config_loader import ConfigLoader
    from shared.enhancement_loader import EnhancementLoader
    from shared.output import Output
    from shared.tool_metadata import ToolMetadata
except ImportError:
    # If even path_utils can't be imported, provide a fallback error
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

# Tool metadata
__version__ = "0.1.0"
TOOL_NAME = "template-tool"


# --- Core functionality ---
def process_input(input_data, config, output):
    """
    Process input with this tool.

    Args:
        input_data: The input data to process
        config: Tool configuration
        output: Output utility for display

    Returns:
        Processed data
    """
    # Implement tool-specific logic here
    output.info(f"Processing input: {input_data}")

    # Demonstrate progress bar if available
    if hasattr(output, "create_progress_bar"):
        # Example of using a progress bar for a long-running operation
        progress = output.create_progress_bar(total=100, desc="Processing data")

        # Simulate processing steps
        for i in range(100):
            # Update progress bar
            progress.update(1)
            # Sleep briefly to simulate work
            time.sleep(0.01)

        # Always close the progress bar when done
        progress.close()

    return input_data


# --- Dependency checking ---
def check_dependencies(output=None):
    """Check status of optional dependencies"""
    enhancer = EnhancementLoader(TOOL_NAME)
    enhancer.check_dependency("rich", "Rich output formatting")
    # Add other optional dependencies here

    if output and hasattr(output, "print_key_value_section"):
        # Create a dictionary of dependencies with their status
        dependencies = {
            key: "Available" if value else "Missing"
            for key, value in enhancer.dependencies.items()
        }

        output.print_key_value_section(
            f"Optional Dependencies for {TOOL_NAME}", dependencies, sort_keys=True
        )

        # Create a list of missing dependencies for installation instructions
        missing = enhancer.get_missing_dependencies()
        if missing:
            output.info("\nTo enable all features, install missing dependencies:")

            if hasattr(output, "print_list"):
                # Display as a list with pip install commands
                install_commands = [f"pip install {dep}" for dep in missing]
                output.print_list("Install Commands", install_commands)
            else:
                # Fallback to simple output
                output.info(f"  pip install {' '.join(missing)}")
    else:
        # Fallback to original method
        enhancer.print_status()


# --- CLI ---
def main():
    """
    CLI entry point for template-tool.
    Uses shared utilities for configuration, output, and enhancement detection.
    """
    # Initialize metadata
    metadata = ToolMetadata.for_current_tool(
        TOOL_NAME, __version__, sys.modules[__name__]
    )

    # Use the shared ArgumentParser
    arg_parser = ArgumentParser(
        tool_name=TOOL_NAME,
        description=metadata.description,
        epilog=metadata.get_help_text(),
        version=__version__,
    )

    # Add tool-specific arguments
    arg_parser.parser.add_argument(
        "input",
        nargs="?",
        help="Input to process",
    )
    arg_parser.parser.add_argument("--config", help="Path to configuration file")
    arg_parser.parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    arg_parser.parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of moving them",
    )
    arg_parser.parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Process subdirectories recursively",
    )
    arg_parser.parser.add_argument(
        "--check-deps", action="store_true", help="Check optional dependency status"
    )

    # Parse arguments
    args = arg_parser.parser.parse_args()

    # Initialize output handling
    output = Output(TOOL_NAME, verbose=False)

    # Check dependencies if requested
    if args.check_deps:
        check_dependencies(output)
        return

    # Display banner with metadata
    output.banner(
        TOOL_NAME,
        __version__,
        {
            "Description": metadata.description,
        },
    )

    # Load configuration
    config_loader = ConfigLoader(TOOL_NAME)
    if args.config:
        config_loader.add_config_file(Path(args.config))
    config = config_loader.load_config()

    # Process input
    if args.input:
        output.task_start("Processing input", args.input)
        result = process_input(args.input, config, output)
        output.task_complete("Processing input", "Completed successfully")

        # Use new output methods if available
        if hasattr(output, "print_key_value_section"):
            output.print_key_value_section(
                "Results",
                {
                    "Input": args.input,
                    "Result": str(result),
                    "Dry Run": "Yes" if args.dry_run else "No",
                    "Copy Mode": "Yes" if args.copy else "No",
                    "Recursive": "Yes" if args.recursive else "No",
                },
            )
        else:
            # Fallback to basic output
            output.header("Results")
            output.item("Input", args.input)
            output.item("Result", str(result))
    else:
        output.error("No input provided")
        arg_parser.parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
