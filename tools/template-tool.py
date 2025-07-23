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
from pathlib import Path
from typing import Any, Dict

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
def process_input(input_data: Any, config: Dict[str, Any], output: Output) -> Any:
    """
    Process input data according to configuration.

    Args:
        input_data: The input data to process
        config: Tool configuration
        output: Output utility for display

    Returns:
        Processed data
    """
    # Implement tool-specific logic here
    output.info(f"Processing input: {input_data}")
    return input_data


# --- Dependency checking ---
def check_dependencies():
    """Check status of optional dependencies"""
    enhancer = EnhancementLoader(TOOL_NAME)
    enhancer.check_dependency("rich", "Rich output formatting")
    # Add other optional dependencies here
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

    # Check dependencies if requested
    if args.check_deps:
        check_dependencies()
        return

    # Initialize output handling
    output = Output(TOOL_NAME, verbose=False)

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

        output.header("Results")
        output.item("Input", args.input)
        output.item("Result", str(result))
    else:
        output.error("No input provided")
        arg_parser.parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
