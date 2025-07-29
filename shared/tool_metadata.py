#!/usr/bin/env python3
"""
Tool metadata utilities for IntermCLI tools.
Provides consistent version and documentation handling.
"""
from typing import Any, List, Optional


class ToolMetadata:
    def __init__(
        self,
        tool_name: str,
        version: str,
        description: str,
        examples: Optional[List[str]] = None,
    ):
        """
        Initialize tool metadata.

        Args:
            tool_name: Name of the tool
            version: Tool version
            description: Short description of the tool
            examples: List of example commands
        """
        self.tool_name = tool_name
        self.version = version
        self.description = description
        self.examples = examples or []

    def get_full_name(self) -> str:
        """Get the full name with version."""
        return f"{self.tool_name} v{self.version}"

    def get_banner(self) -> str:
        """Get a banner for the tool."""
        return f"🔧 {self.tool_name} v{self.version} - {self.description}"

    def get_help_text(self) -> str:
        """Get formatted help text with description and examples."""
        help_text = [
            f"{self.description}",
            "",
            "Examples:",
        ]
        for example in self.examples:
            help_text.append(f"  {example}")
        return "\n".join(help_text)

    @classmethod
    def from_module_docstring(
        cls, tool_name: str, version: str, docstring: str
    ) -> "ToolMetadata":
        """
        Create tool metadata from a module docstring.

        Args:
            tool_name: Name of the tool
            version: Tool version
            docstring: Module docstring to parse

        Returns:
            ToolMetadata object
        """
        # Extract the first paragraph as the description
        lines = docstring.strip().split("\n")
        description = lines[0] if lines else ""

        # Extract examples
        examples = []
        in_examples = False
        for line in lines:
            if line.strip().lower().startswith("example"):
                in_examples = True
                continue
            if in_examples and line.strip():
                examples.append(line.strip())

        return cls(tool_name, version, description, examples)

    @classmethod
    def for_current_tool(
        cls, tool_name: str, version: str, module: Any
    ) -> "ToolMetadata":
        """
        Create tool metadata for the current tool.

        Args:
            tool_name: Name of the tool
            version: Tool version
            module: The current module (__main__)

        Returns:
            ToolMetadata object
        """
        return cls.from_module_docstring(tool_name, version, module.__doc__ or "")
