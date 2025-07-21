#!/usr/bin/env python3
"""
Tests for shared utilities in IntermCLI.
"""
import os
import sys
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.config_loader import ConfigLoader
from shared.enhancement_loader import EnhancementLoader
from shared.network_utils import NetworkUtils
from shared.output import Output


class TestConfigLoader(unittest.TestCase):
    """Tests for the ConfigLoader utility."""

    def setUp(self):
        self.config_loader = ConfigLoader("test-tool")

    def test_get_default_config(self):
        """Test that default config is returned correctly."""
        config = self.config_loader._get_default_config()
        self.assertIsInstance(config, dict)
        self.assertIn("version", config)
        self.assertIn("common", config)

    def test_get_config_files(self):
        """Test that config files are found correctly."""
        config_files = self.config_loader._get_config_files()
        self.assertIsInstance(config_files, list)

        # Each item should be a tuple of (Path, str)
        for file_info in config_files:
            self.assertIsInstance(file_info, tuple)
            self.assertEqual(len(file_info), 2)
            self.assertIsInstance(file_info[0], Path)
            self.assertIsInstance(file_info[1], str)

    def test_convert_env_value(self):
        """Test environment value conversion."""
        self.assertEqual(self.config_loader._convert_env_value("true"), True)
        self.assertEqual(self.config_loader._convert_env_value("false"), False)
        self.assertEqual(self.config_loader._convert_env_value("42"), 42)
        self.assertEqual(self.config_loader._convert_env_value("3.14"), 3.14)
        self.assertEqual(self.config_loader._convert_env_value("hello"), "hello")


class TestEnhancementLoader(unittest.TestCase):
    """Tests for the EnhancementLoader utility."""

    def setUp(self):
        self.enhancement_loader = EnhancementLoader("test-tool")

    def test_check_dependency(self):
        """Test dependency checking."""
        # os should always be available
        self.assertTrue(self.enhancement_loader.check_dependency("os"))
        # nonexistent module should not be available
        self.assertFalse(self.enhancement_loader.check_dependency("nonexistent_module"))

    def test_register_feature(self):
        """Test feature registration."""
        # Register dependencies
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("nonexistent_module")

        # Register features
        available = self.enhancement_loader.register_feature("feature1", ["os"])
        unavailable = self.enhancement_loader.register_feature(
            "feature2", ["nonexistent_module"]
        )
        mixed = self.enhancement_loader.register_feature(
            "feature3", ["os", "nonexistent_module"]
        )

        self.assertTrue(available)
        self.assertFalse(unavailable)
        self.assertFalse(mixed)

    def test_get_missing_dependencies(self):
        """Test getting missing dependencies."""
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("sys")
        self.enhancement_loader.check_dependency("nonexistent_module1")
        self.enhancement_loader.check_dependency("nonexistent_module2")

        missing = self.enhancement_loader.get_missing_dependencies()
        self.assertEqual(len(missing), 2)
        self.assertIn("nonexistent_module1", missing)
        self.assertIn("nonexistent_module2", missing)


class TestOutput(unittest.TestCase):
    """Tests for the Output utility."""

    def setUp(self):
        self.output = Output("test-tool", use_rich=False)

    def test_simple_table(self):
        """Test simple table generation."""
        headers = ["Name", "Age", "Location"]
        rows = [
            ["Alice", 30, "New York"],
            ["Bob", 25, "San Francisco"],
            ["Charlie", 35, "Seattle"],
        ]

        # This is hard to test, but at least make sure it doesn't error
        self.output._print_simple_table(headers, rows)

    def test_supports_color(self):
        """Test color support detection."""
        # This will depend on the environment, but the function shouldn't error
        result = self.output._supports_color()
        self.assertIsInstance(result, bool)


class TestNetworkUtils(unittest.TestCase):
    """Tests for the NetworkUtils utility."""

    def setUp(self):
        self.network_utils = NetworkUtils(timeout=1.0)  # Short timeout for tests

    def test_get_ip(self):
        """Test IP address lookup."""
        # This should return something for localhost
        result = self.network_utils.get_ip("localhost")
        self.assertIsNotNone(result)
        self.assertTrue(result == "127.0.0.1" or result.startswith("::1"))

    def test_extract_title(self):
        """Test HTML title extraction."""
        html = "<html><head><title>Test Page</title></head><body>Content</body></html>"
        title = self.network_utils._extract_title(html)
        self.assertEqual(title, "Test Page")

        # No title
        html = "<html><head></head><body>Content</body></html>"
        title = self.network_utils._extract_title(html)
        self.assertIsNone(title)


if __name__ == "__main__":
    unittest.main()
