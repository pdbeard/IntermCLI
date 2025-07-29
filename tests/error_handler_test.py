#!/usr/bin/env python3
"""
Tests for the ErrorHandler shared utility.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.error_handler import ErrorHandler
from shared.output import Output


class TestErrorHandler(unittest.TestCase):
    """Tests for the ErrorHandler utility."""

    def setUp(self):
        """Set up the test environment."""
        self.mock_output = MagicMock(spec=Output)
        self.error_handler = ErrorHandler(self.mock_output)

        # Non-exiting error handler for testing
        self.non_exit_handler = ErrorHandler(self.mock_output, exit_on_critical=False)

        # Exiting error handler for testing
        self.exit_handler = ErrorHandler(self.mock_output, exit_on_critical=True)

    def test_init(self):
        """Test initialization of ErrorHandler."""
        self.assertEqual(self.error_handler.output, self.mock_output)
        self.assertFalse(self.error_handler.exit_on_critical)

        self.assertTrue(self.exit_handler.exit_on_critical)

    def test_non_critical_error_codes(self):
        """Test non-critical error codes."""
        # Create an ErrorHandler with exit_on_critical=False
        mock_output = MagicMock(spec=Output)
        handler = ErrorHandler(mock_output, exit_on_critical=False)

        # Mock sys.exit to ensure it's never called
        with patch("sys.exit") as mock_exit:
            # Even with critical codes, exit should not be called
            handler.exit_if_critical("config:not_found")
            mock_exit.assert_not_called()

            # Non-critical codes also should not call sys.exit
            handler.exit_if_critical("network:timeout")
            mock_exit.assert_not_called()

    def test_handle_generic(self):
        """Test generic error handling."""
        error = ValueError("Test error")
        context = "testing context"

        msg, code = self.error_handler._handle_generic(context, error)

        self.assertTrue(context in msg)
        self.assertTrue("ValueError" in code)
        # Verify output.error was called
        self.mock_output.error.assert_called_once()

    def test_handle_file_operation(self):
        """Test handling file operation errors."""
        path = Path("/test/file.txt")

        # Test FileNotFoundError
        error = FileNotFoundError("No such file")
        msg, code = self.error_handler.handle_file_operation(path, error)
        self.assertTrue("not found" in msg.lower())
        self.assertEqual(code, "file:not_found")

        # Test PermissionError
        error = PermissionError("Permission denied")
        msg, code = self.error_handler.handle_file_operation(path, error)
        self.assertTrue("permission" in msg.lower())
        self.assertEqual(code, "file:permission_denied")

        # Test IOError
        error = IOError("IO Error")
        msg, code = self.error_handler.handle_file_operation(path, error)
        self.assertTrue("failed to access" in msg.lower() or "error" in msg.lower())
        self.assertEqual(code, "file:OSError")  # IOError is an alias for OSError

        # Test other exceptions
        error = ValueError("Value Error")
        msg, code = self.error_handler.handle_file_operation(path, error)
        self.assertTrue("failed to access" in msg.lower() or "error" in msg.lower())
        self.assertEqual(code, "file:ValueError")

    def test_handle_network_operation(self):
        """Test handling network operation errors."""
        # Test ConnectionError
        error = ConnectionError("Connection refused")
        msg, code = self.error_handler.handle_network_operation("test.com", error)
        self.assertTrue("connect" in msg.lower())
        self.assertEqual(code, "network:connection_error")

        # Test TimeoutError
        error = TimeoutError("Timeout")
        msg, code = self.error_handler.handle_network_operation("test.com", error)
        self.assertTrue("timed out" in msg.lower())
        self.assertEqual(code, "network:timeout")

        # Test other exceptions
        error = ValueError("Value Error")
        msg, code = self.error_handler.handle_network_operation("test.com", error)
        self.assertTrue("error" in msg.lower())
        self.assertEqual(code, "network:ValueError")

    def test_handle_config_error(self):
        """Test handling configuration errors."""
        config_file = Path("/test/config.toml")

        # Test FileNotFoundError
        error = FileNotFoundError("No such file")
        msg, code = self.error_handler.handle_config_error(config_file, error)
        self.assertTrue("configuration file not found" in msg.lower())
        self.assertEqual(code, "config:not_found")

        # Test PermissionError
        error = PermissionError("Permission denied")
        msg, code = self.error_handler.handle_config_error(config_file, error)
        self.assertTrue("permission" in msg.lower())
        self.assertEqual(code, "config:permission_denied")

        # Test ValueError (might be handled as a generic error)
        error = ValueError("Invalid TOML")
        msg, code = self.error_handler.handle_config_error(config_file, error)
        self.assertTrue(
            "error in configuration" in msg.lower() or "invalid" in msg.lower()
        )
        self.assertTrue(code.startswith("config:"))

        # Create a mock error that looks like a TomlDecodeError
        class TomlDecodeError(Exception):
            pass

        error = TomlDecodeError("Invalid TOML")
        msg, code = self.error_handler.handle_config_error(config_file, error)
        self.assertTrue("invalid" in msg.lower() or "error" in msg.lower())
        self.assertTrue(code.startswith("config:"))

    def test_critical_error_codes(self):
        """Test identifying critical error codes."""
        # Create our own ErrorHandler for this test to mock exit_if_critical
        mock_output = MagicMock(spec=Output)
        handler = ErrorHandler(mock_output, exit_on_critical=True)

        # Replace sys.exit with a mock that raises an exception
        with patch("sys.exit") as mock_exit:
            # Critical codes should call sys.exit
            handler.exit_if_critical("config:not_found")
            mock_exit.assert_called_once()
            mock_exit.reset_mock()

            # Non-critical codes should not call sys.exit
            handler.exit_if_critical("network:timeout")
            mock_exit.assert_not_called()

    @patch("sys.exit")
    def test_non_exit_handler_behavior(self, mock_exit):
        """Test that non-exit handler doesn't exit on critical errors."""
        # Using a critical error (404)
        error = FileNotFoundError("No such file")
        self.non_exit_handler.handle_file_operation(Path("/test.txt"), error)

        # Check that exit was not called
        mock_exit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
