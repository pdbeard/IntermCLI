#!/usr/bin/env python3
"""
Tests for the PathUtils shared utility.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.path_utils import (
    add_shared_path,
    ensure_shared_imports,
    require_shared_utilities,
)


class TestPathUtils(unittest.TestCase):
    """Tests for the PathUtils utility."""

    def setUp(self):
        """Set up the test environment."""
        # Save original sys.path
        self.original_path = sys.path.copy()

    def tearDown(self):
        """Clean up after tests."""
        # Restore original sys.path
        sys.path = self.original_path

    def test_add_shared_path(self):
        """Test adding shared path to sys.path."""
        # Get the path to the intermCLI root directory
        root_dir = Path(__file__).resolve().parents[1]

        # Remember the original path
        orig_path = sys.path.copy()

        # Call the function
        add_shared_path()

        # Check that the path is present
        self.assertIn(str(root_dir), sys.path)

        # Restore original path to avoid side effects
        sys.path = orig_path

    @patch("importlib.util.find_spec")
    def test_ensure_shared_imports_available(self, mock_find_spec):
        """Test ensuring shared imports when they are available."""
        # Mock find_spec to return a non-None value
        mock_find_spec.return_value = MagicMock()

        # Call the function
        result = ensure_shared_imports()

        # Check that the function returns True
        self.assertTrue(result)
        # Check that find_spec was called with 'shared'
        mock_find_spec.assert_called_with("shared")
        # add_shared_path should not have been called
        self.assertEqual(mock_find_spec.call_count, 1)

    @patch("importlib.util.find_spec")
    @patch("shared.path_utils.add_shared_path")
    def test_ensure_shared_imports_unavailable_then_available(
        self, mock_add_shared_path, mock_find_spec
    ):
        """Test ensuring shared imports when they are initially unavailable but become available."""
        # Mock find_spec to return None the first time, then a non-None value
        mock_find_spec.side_effect = [None, MagicMock()]

        # Call the function
        result = ensure_shared_imports()

        # Check that the function returns True
        self.assertTrue(result)
        # Check that find_spec was called twice
        self.assertEqual(mock_find_spec.call_count, 2)
        # add_shared_path should have been called
        mock_add_shared_path.assert_called_once()

    @patch("importlib.util.find_spec")
    @patch("shared.path_utils.add_shared_path")
    def test_ensure_shared_imports_always_unavailable(
        self, mock_add_shared_path, mock_find_spec
    ):
        """Test ensuring shared imports when they are always unavailable."""
        # Mock find_spec to always return None
        mock_find_spec.side_effect = [None, None]

        # Call the function
        result = ensure_shared_imports()

        # Check that the function returns False
        self.assertFalse(result)
        # Check that find_spec was called twice
        self.assertEqual(mock_find_spec.call_count, 2)
        # add_shared_path should have been called
        mock_add_shared_path.assert_called_once()

    @patch("shared.path_utils.ensure_shared_imports")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_require_shared_utilities_available(
        self, mock_exit, mock_print, mock_ensure_shared_imports
    ):
        """Test requiring shared utilities when they are available."""
        # Mock ensure_shared_imports to return True
        mock_ensure_shared_imports.return_value = True

        # Call the function
        require_shared_utilities()

        # Check that ensure_shared_imports was called
        mock_ensure_shared_imports.assert_called_once()
        # Check that print was not called
        mock_print.assert_not_called()
        # Check that exit was not called
        mock_exit.assert_not_called()

    @patch("shared.path_utils.ensure_shared_imports")
    @patch("builtins.print")
    @patch("sys.exit")
    def test_require_shared_utilities_unavailable(
        self, mock_exit, mock_print, mock_ensure_shared_imports
    ):
        """Test requiring shared utilities when they are unavailable."""
        # Mock ensure_shared_imports to return False
        mock_ensure_shared_imports.return_value = False

        # Call the function
        require_shared_utilities()

        # Check that ensure_shared_imports was called
        mock_ensure_shared_imports.assert_called_once()
        # Check that print was called
        self.assertTrue(mock_print.called)
        # Check that exit was called with status 1
        mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
