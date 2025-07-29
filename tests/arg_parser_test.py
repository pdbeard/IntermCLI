#!/usr/bin/env python3
"""
Tests for the ArgumentParser shared utility.
"""
import unittest
from argparse import ArgumentParser as ArgParser
from unittest.mock import patch

from shared.arg_parser import ArgumentParser


class TestArgumentParser(unittest.TestCase):
    """Tests for the ArgumentParser utility."""

    def setUp(self):
        """Set up the test environment."""
        self.tool_name = "test-tool"
        self.description = "Test tool description"
        self.epilog = "Test epilog"
        self.version = "1.0.0"
        self.arg_parser = ArgumentParser(
            tool_name=self.tool_name,
            description=self.description,
            epilog=self.epilog,
            version=self.version,
        )

    def test_init(self):
        """Test initialization of ArgumentParser."""
        self.assertEqual(self.arg_parser.tool_name, self.tool_name)
        self.assertEqual(self.arg_parser.version, self.version)
        self.assertIsInstance(self.arg_parser.parser, ArgParser)

    def test_add_common_arguments(self):
        """Test adding common arguments."""
        self.arg_parser.add_common_arguments()

        # Parse args to see if verbose is recognized
        args = self.arg_parser.parser.parse_args([])
        self.assertFalse(args.verbose)

        # Parse with verbose flag
        args = self.arg_parser.parser.parse_args(["--verbose"])
        self.assertTrue(args.verbose)

        # Parse with short verbose flag
        args = self.arg_parser.parser.parse_args(["-v"])
        self.assertTrue(args.verbose)

    def test_add_common_arguments_with_options(self):
        """Test adding common arguments including optional flags."""
        self.arg_parser.add_common_arguments()

        # Parse args to see if flags are recognized
        args = self.arg_parser.parser.parse_args([])
        self.assertFalse(args.verbose)
        self.assertIsNone(args.config)
        self.assertFalse(args.no_color)
        self.assertFalse(args.check_deps)

        # Parse with various flags
        args = self.arg_parser.parser.parse_args(["--verbose"])
        self.assertTrue(args.verbose)

        args = self.arg_parser.parser.parse_args(["--config", "test.toml"])
        self.assertEqual(args.config, "test.toml")

        args = self.arg_parser.parser.parse_args(["--no-color"])
        self.assertTrue(args.no_color)

        args = self.arg_parser.parser.parse_args(["--check-deps"])
        self.assertTrue(args.check_deps)

    def test_add_positional_argument(self):
        """Test adding positional arguments."""
        self.arg_parser.add_positional_argument("test", "Test argument")

        # Parse args to see if positional argument is recognized
        args = self.arg_parser.parser.parse_args(["value"])
        self.assertEqual(args.test, "value")

    def test_add_output_arguments(self):
        """Test adding output arguments."""
        self.arg_parser.add_output_arguments()

        # Parse args to see if output flags are recognized
        args = self.arg_parser.parser.parse_args([])
        self.assertEqual(args.output, "text")
        self.assertIsNone(args.output_file)
        self.assertFalse(args.quiet)

        # Parse with output format
        args = self.arg_parser.parser.parse_args(["--output", "json"])
        self.assertEqual(args.output, "json")

        # Parse with output file
        args = self.arg_parser.parser.parse_args(["--output-file", "test.txt"])
        self.assertEqual(args.output_file, "test.txt")

        # Parse with quiet flag
        args = self.arg_parser.parser.parse_args(["--quiet"])
        self.assertTrue(args.quiet)

    def test_add_config_argument(self):
        """Test adding config argument."""
        self.arg_parser.add_config_argument()

        # Parse args to see if config flags are recognized
        args = self.arg_parser.parser.parse_args([])
        self.assertFalse(args.show_config)

        # Parse with show config flag
        args = self.arg_parser.parser.parse_args(["--show-config"])
        self.assertTrue(args.show_config)

    @patch("sys.argv", ["test-tool", "--version"])
    def test_version_argument(self):
        """Test version argument handling."""
        # Testing the version action requires a bit of mocking
        with self.assertRaises(SystemExit) as cm:
            self.arg_parser.parser.parse_args()

        self.assertEqual(cm.exception.code, 0)

    def test_parse_args_wrapper(self):
        """Test the parse_args wrapper method."""
        # Add some arguments
        self.arg_parser.add_common_arguments()

        # Test with arguments
        with patch("sys.argv", ["test-tool", "--verbose"]):
            args = self.arg_parser.parse_args()
            self.assertTrue(args.verbose)


if __name__ == "__main__":
    unittest.main()
