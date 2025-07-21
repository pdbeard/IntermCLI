#!/usr/bin/env python3
"""
Argument parser utilities for IntermCLI tools.
Provides consistent argument parsing with common patterns.
"""
import argparse
from typing import Any, Callable, Dict, List, Optional, Union


class ArgumentParser:
    def __init__(
        self,
        tool_name: str,
        description: str,
        epilog: Optional[str] = None,
        version: str = "1.0.0",
    ):
        """
        Initialize argument parser for a tool.

        Args:
            tool_name: Name of the tool
            description: Tool description
            epilog: Optional epilog text
            version: Tool version
        """
        self.tool_name = tool_name
        self.version = version

        # Create parser
        self.parser = argparse.ArgumentParser(
            description=description,
            epilog=epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        # Add common arguments
        self.parser.add_argument(
            "--version",
            action="version",
            version=f"{tool_name} {version}",
            help="Show version information and exit",
        )

    def add_common_arguments(self) -> None:
        """Add common arguments used across most tools."""
        self.parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )

        self.parser.add_argument(
            "--config",
            metavar="PATH",
            help="Path to config file (default: ~/.config/intermcli/{tool}.toml)",
        )

        self.parser.add_argument(
            "--no-color", action="store_true", help="Disable colored output"
        )

        self.parser.add_argument(
            "--check-deps",
            action="store_true",
            help="Check for optional dependencies and exit",
        )

    def add_output_arguments(self) -> None:
        """Add output-related arguments."""
        output_group = self.parser.add_argument_group("Output Options")

        output_group.add_argument(
            "--output",
            choices=["text", "json", "csv"],
            default="text",
            help="Output format (default: text)",
        )

        output_group.add_argument(
            "--output-file",
            metavar="PATH",
            help="Write output to file instead of stdout",
        )

        output_group.add_argument(
            "--quiet", "-q", action="store_true", help="Suppress informational output"
        )

    def add_config_argument(self) -> None:
        """Add argument to show current configuration."""
        self.parser.add_argument(
            "--show-config",
            action="store_true",
            help="Show current configuration and exit",
        )

    def add_positional_argument(
        self,
        name: str,
        help_text: str,
        nargs: Union[int, str] = None,
        default: Any = None,
        type: Callable = str,
    ) -> None:
        """
        Add a positional argument.

        Args:
            name: Argument name
            help_text: Help text
            nargs: Number of arguments (default: None)
            default: Default value (default: None)
            type: Type converter (default: str)
        """
        kwargs = {"help": help_text, "type": type}
        if nargs is not None:
            kwargs["nargs"] = nargs
        if default is not None:
            kwargs["default"] = default

        self.parser.add_argument(name, **kwargs)

    def add_flag(
        self, name: str, help_text: str, short_name: Optional[str] = None
    ) -> None:
        """
        Add a boolean flag argument.

        Args:
            name: Long name (without --)
            help_text: Help text
            short_name: Optional short name (without -)
        """
        if short_name:
            self.parser.add_argument(
                f"--{name}", f"-{short_name}", action="store_true", help=help_text
            )
        else:
            self.parser.add_argument(f"--{name}", action="store_true", help=help_text)

    def add_option(
        self,
        name: str,
        help_text: str,
        short_name: Optional[str] = None,
        default: Any = None,
        type: Callable = str,
        choices: Optional[List[Any]] = None,
    ) -> None:
        """
        Add an option argument.

        Args:
            name: Long name (without --)
            help_text: Help text
            short_name: Optional short name (without -)
            default: Default value
            type: Type converter
            choices: Optional list of valid choices
        """
        kwargs = {"help": help_text, "type": type}

        if default is not None:
            kwargs["default"] = default

        if choices is not None:
            kwargs["choices"] = choices

        if short_name:
            self.parser.add_argument(f"--{name}", f"-{short_name}", **kwargs)
        else:
            self.parser.add_argument(f"--{name}", **kwargs)

    def parse_args(self) -> argparse.Namespace:
        """
        Parse command line arguments.

        Returns:
            Parsed arguments namespace
        """
        return self.parser.parse_args()

    def parse_args_as_dict(self) -> Dict[str, Any]:
        """
        Parse command line arguments as dictionary.

        Returns:
            Dictionary of argument name to value
        """
        args = self.parser.parse_args()
        return vars(args)


def create_arg_parser(
    tool_name: str,
    description: str,
    epilog: Optional[str] = None,
    version: str = "1.0.0",
) -> ArgumentParser:
    """
    Helper function to create an argument parser.

    Args:
        tool_name: Name of the tool
        description: Tool description
        epilog: Optional epilog text
        version: Tool version

    Returns:
        ArgumentParser instance
    """
    return ArgumentParser(tool_name, description, epilog, version)
