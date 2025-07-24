#!/usr/bin/env python3
"""
Tests for the shared enhancement_loader module.
"""
import logging
import unittest
from unittest import mock

from shared.enhancement_loader import EnhancementLoader


class TestEnhancementLoader(unittest.TestCase):
    """Test suite for the EnhancementLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.enhancement_loader = EnhancementLoader("test_tool")

    def test_init(self):
        """Test initialization with defaults."""
        loader = EnhancementLoader("test_tool")
        self.assertEqual(loader.tool_name, "test_tool")
        self.assertIsInstance(loader.logger, logging.Logger)
        self.assertEqual(loader.logger.name, "test_tool")
        self.assertEqual(loader.dependencies, {})
        self.assertEqual(loader.features, {})

        # Test with custom logger
        custom_logger = logging.getLogger("custom")
        loader = EnhancementLoader("custom_tool", logger=custom_logger)
        self.assertEqual(loader.tool_name, "custom_tool")
        self.assertEqual(loader.logger, custom_logger)

    def test_get_default_logger(self):
        """Test the default logger creation."""
        logger = self.enhancement_loader._get_default_logger()
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_tool")

    def test_is_module_available_existing(self):
        """Test checking for an existing module."""
        # Test with a module that definitely exists
        self.assertTrue(self.enhancement_loader._is_module_available("os"))
        self.assertTrue(self.enhancement_loader._is_module_available("sys"))
        self.assertTrue(self.enhancement_loader._is_module_available("json"))

    def test_is_module_available_nonexistent(self):
        """Test checking for a non-existent module."""
        # Test with a module that definitely doesn't exist
        self.assertFalse(
            self.enhancement_loader._is_module_available("not_a_real_module_123xyz")
        )

    @mock.patch("importlib.util.find_spec")
    def test_is_module_available_error(self, mock_find_spec):
        """Test handling errors during module checking."""
        # Test with a module that raises an error
        mock_find_spec.side_effect = ImportError("Mock import error")
        self.assertFalse(self.enhancement_loader._is_module_available("error_module"))

    @mock.patch("sys.version_info", (3, 11, 0))
    def test_is_module_available_tomllib(self):
        """Test the special case for tomllib in Python 3.11+."""
        # This should return True for Python 3.11+
        self.assertTrue(self.enhancement_loader._is_module_available("tomllib"))

    @mock.patch("sys.version_info", (3, 10, 0))
    @mock.patch("importlib.util.find_spec")
    def test_is_module_available_tomllib_older_python(self, mock_find_spec):
        """Test the special case for tomllib in Python < 3.11."""
        # Set up the mock to return None for tomllib
        mock_find_spec.return_value = None

        # This should call find_spec for Python < 3.11
        self.assertFalse(self.enhancement_loader._is_module_available("tomllib"))
        mock_find_spec.assert_called_once_with("tomllib")

    def test_check_dependency(self):
        """Test checking and registering dependencies."""
        # Check a dependency that exists
        result = self.enhancement_loader.check_dependency("os")
        self.assertTrue(result)
        self.assertEqual(self.enhancement_loader.dependencies["os"], True)

        # Check a dependency with an alias
        result = self.enhancement_loader.check_dependency("sys", alias="system")
        self.assertTrue(result)
        self.assertEqual(self.enhancement_loader.dependencies["system"], True)

        # Check a dependency that doesn't exist
        result = self.enhancement_loader.check_dependency("not_a_real_module_123xyz")
        self.assertFalse(result)
        self.assertEqual(
            self.enhancement_loader.dependencies["not_a_real_module_123xyz"], False
        )

    def test_register_feature_all_available(self):
        """Test registering a feature with all dependencies available."""
        # Register dependencies
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("sys")

        # Register feature
        result = self.enhancement_loader.register_feature("test_feature", ["os", "sys"])

        self.assertTrue(result)
        self.assertEqual(self.enhancement_loader.features["test_feature"], True)

    def test_register_feature_missing_dependency(self):
        """Test registering a feature with a missing dependency."""
        # Register one dependency
        self.enhancement_loader.check_dependency("os")

        # Try to register feature with a dependency that hasn't been checked
        with mock.patch.object(
            self.enhancement_loader.logger, "warning"
        ) as mock_warning:
            result = self.enhancement_loader.register_feature(
                "test_feature", ["os", "unknown_dep"]
            )

        # Should auto-check the missing dependency
        self.assertFalse(result)
        self.assertEqual(self.enhancement_loader.features["test_feature"], False)
        mock_warning.assert_called_once()

    def test_register_feature_some_unavailable(self):
        """Test registering a feature with some unavailable dependencies."""
        # Register dependencies with one unavailable
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("not_a_real_module_123xyz")

        # Register feature
        result = self.enhancement_loader.register_feature(
            "test_feature", ["os", "not_a_real_module_123xyz"]
        )

        self.assertFalse(result)
        self.assertEqual(self.enhancement_loader.features["test_feature"], False)

    def test_register_enhancement_available(self):
        """Test registering an enhancement that is available."""
        # Register dependencies
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("sys")

        # Create a mock callback
        callback = mock.Mock()

        # Register enhancement
        self.enhancement_loader.register_enhancement(
            "test_enhancement", callback, ["os", "sys"]
        )

        # Check that the enhancement was registered
        self.assertTrue(self.enhancement_loader.features["test_enhancement"])
        self.assertEqual(
            self.enhancement_loader._enhancement_callbacks["test_enhancement"], callback
        )

    def test_register_enhancement_unavailable(self):
        """Test registering an enhancement that is unavailable."""
        # Register dependencies with one unavailable
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("not_a_real_module_123xyz")

        # Create a mock callback
        callback = mock.Mock()

        # Register enhancement
        self.enhancement_loader.register_enhancement(
            "test_enhancement", callback, ["os", "not_a_real_module_123xyz"]
        )

        # Check that the enhancement was not registered
        self.assertFalse(self.enhancement_loader.features["test_enhancement"])
        self.assertNotIn(
            "test_enhancement", self.enhancement_loader._enhancement_callbacks
        )

    def test_apply_enhancements(self):
        """Test applying registered enhancements."""
        # Register dependencies
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("sys")

        # Create mock callbacks that return values
        callback1 = mock.Mock(return_value={"result": "value1"})
        callback2 = mock.Mock(return_value={"result": "value2"})

        # Register enhancements
        self.enhancement_loader.register_enhancement("enhancement1", callback1, ["os"])
        self.enhancement_loader.register_enhancement("enhancement2", callback2, ["sys"])

        # Apply enhancements with kwargs
        kwargs = {"arg1": "value1", "arg2": "value2"}
        results = self.enhancement_loader.apply_enhancements(**kwargs)

        # Check that callbacks were called with kwargs
        callback1.assert_called_once_with(**kwargs)
        callback2.assert_called_once_with(**kwargs)

        # Check results
        self.assertEqual(
            results,
            {
                "enhancement1": {"result": "value1"},
                "enhancement2": {"result": "value2"},
            },
        )

    def test_apply_enhancements_empty(self):
        """Test applying enhancements when none are registered."""
        results = self.enhancement_loader.apply_enhancements(arg="value")
        self.assertEqual(results, {})

    def test_get_missing_dependencies(self):
        """Test getting missing dependencies."""
        # Register dependencies with some missing
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("not_real_1", alias="Missing 1")
        self.enhancement_loader.check_dependency("not_real_2", alias="Missing 2")

        # Get missing dependencies
        missing = self.enhancement_loader.get_missing_dependencies()

        # Check results
        self.assertEqual(len(missing), 2)
        self.assertIn("Missing 1", missing)
        self.assertIn("Missing 2", missing)
        self.assertNotIn("os", missing)

    def test_get_missing_dependencies_empty(self):
        """Test getting missing dependencies when none are missing."""
        # Register only available dependencies
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("sys")

        # Get missing dependencies
        missing = self.enhancement_loader.get_missing_dependencies()

        # Check results
        self.assertEqual(len(missing), 0)

    def test_print_status_deps_only(self):
        """Test printing dependency status."""
        # Register dependencies
        self.enhancement_loader.check_dependency("os")
        self.enhancement_loader.check_dependency("not_real", alias="Missing Dep")

        # Register features
        self.enhancement_loader.register_feature("Feature 1", ["os"])
        self.enhancement_loader.register_feature("Feature 2", ["Missing Dep"])
        self.enhancement_loader.register_feature("Feature 3", ["os", "Missing Dep"])

        # Mock the logger
        with mock.patch.object(self.enhancement_loader.logger, "info") as mock_info:
            self.enhancement_loader.print_status(show_features=False, show_deps=True)

        # Check that the logger was called with appropriate messages
        self.assertTrue(mock_info.call_count >= 3)  # At least 3 info messages

    def test_print_status_with_missing_deps(self):
        """Test printing status with missing dependencies."""
        # Register missing dependencies
        self.enhancement_loader.check_dependency("not_real_1", alias="Missing 1")
        self.enhancement_loader.check_dependency("not_real_2", alias="Missing 2")

        # Mock the logger
        with mock.patch.object(self.enhancement_loader.logger, "info") as mock_info:
            self.enhancement_loader.print_status()

        # Check that the logger was called with installation instructions
        self.assertTrue(mock_info.call_count >= 2)  # At least 2 info messages

        # Check that pip install command was output
        pip_install_message = False
        for call in mock_info.call_args_list:
            args, _ = call
            if "pip install" in args[0]:
                pip_install_message = True
                break

        self.assertTrue(pip_install_message)


if __name__ == "__main__":
    unittest.main()
