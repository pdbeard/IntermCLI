#!/usr/bin/env python3
"""
Tests for the ToolMetadata shared utility.
"""
import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.tool_metadata import ToolMetadata


class TestToolMetadata(unittest.TestCase):
    """Tests for the ToolMetadata utility."""

    def setUp(self):
        """Set up the test environment."""
        self.tool_name = "test-tool"
        self.version = "1.0.0"
        self.description = "Test tool description"
        self.examples = ["test-tool example1", "test-tool --flag example2"]
        self.metadata = ToolMetadata(
            tool_name=self.tool_name,
            version=self.version,
            description=self.description,
            examples=self.examples,
        )

    def test_init(self):
        """Test initialization of ToolMetadata."""
        self.assertEqual(self.metadata.tool_name, self.tool_name)
        self.assertEqual(self.metadata.version, self.version)
        self.assertEqual(self.metadata.description, self.description)
        self.assertEqual(self.metadata.examples, self.examples)

        # Test with default examples
        metadata = ToolMetadata(
            tool_name=self.tool_name, version=self.version, description=self.description
        )
        self.assertEqual(metadata.examples, [])

    def test_get_full_name(self):
        """Test getting the full name."""
        expected = f"{self.tool_name} v{self.version}"
        self.assertEqual(self.metadata.get_full_name(), expected)

    def test_get_banner(self):
        """Test getting the banner."""
        expected = f"🔧 {self.tool_name} v{self.version} - {self.description}"
        self.assertEqual(self.metadata.get_banner(), expected)

    def test_get_help_text(self):
        """Test getting the help text."""
        help_text = self.metadata.get_help_text()

        # Check that description is included
        self.assertIn(self.description, help_text)

        # Check that examples are included
        self.assertIn("Examples:", help_text)
        for example in self.examples:
            self.assertIn(example, help_text)

    def test_from_module_docstring(self):
        """Test creating metadata from a module docstring."""
        docstring = """Test module description.

        More detailed information about the module.

        Example usage:
            test-tool example1
            test-tool --flag example2
        """

        metadata = ToolMetadata.from_module_docstring(
            self.tool_name, self.version, docstring
        )

        self.assertEqual(metadata.tool_name, self.tool_name)
        self.assertEqual(metadata.version, self.version)
        self.assertEqual(metadata.description, "Test module description.")
        self.assertEqual(len(metadata.examples), 2)
        self.assertEqual(metadata.examples[0], "test-tool example1")
        self.assertEqual(metadata.examples[1], "test-tool --flag example2")

    def test_for_current_tool(self):
        """Test creating metadata for the current tool."""

        # Create a mock module
        class MockModule:
            __doc__ = """Test module description.

            More detailed information about the module.

            Example usage:
                test-tool example1
                test-tool --flag example2
            """

        mock_module = MockModule()

        # Call the method
        metadata = ToolMetadata.for_current_tool(
            self.tool_name, self.version, mock_module
        )

        self.assertEqual(metadata.tool_name, self.tool_name)
        self.assertEqual(metadata.version, self.version)
        self.assertEqual(metadata.description, "Test module description.")
        self.assertEqual(len(metadata.examples), 2)


if __name__ == "__main__":
    unittest.main()
