#!/usr/bin/env python3
"""
Tests for the shared output module.
"""
import logging
import sys
import unittest
from io import StringIO
from unittest import mock

# Directly import from shared.output to test individual components
from shared.output import (
    Output,
    RichProgressAdapter,
    SimpleProgressBar,
    setup_tool_output,
)


class TestOutput(unittest.TestCase):
    """Test suite for the output module."""

    def setUp(self):
        """Set up test fixtures."""
        self.output = Output("test_tool")
        # Capture stdout and stderr
        self.stdout_capture = StringIO()
        self.stderr_capture = StringIO()
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture

    def tearDown(self):
        """Tear down test fixtures."""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    def test_init(self):
        """Test initialization with defaults."""
        output = Output("test_tool")
        self.assertEqual(output.tool_name, "test_tool")
        self.assertIsInstance(output.logger, logging.Logger)
        self.assertEqual(output.logger.name, "test_tool")
        self.assertFalse(output.verbose)

        # Test with custom values
        output = Output("custom_tool", use_rich=False, verbose=True)
        self.assertEqual(output.tool_name, "custom_tool")
        self.assertTrue(output.verbose)

    def test_supports_color(self):
        """Test color support detection."""
        # This is mostly environment-dependent, so just ensure it returns a boolean
        result = self.output._supports_color()
        self.assertIsInstance(result, bool)

    def test_info(self):
        """Test info output."""
        # Replace direct logging with a mock to avoid terminal output issues in tests
        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output.logger, "info") as mock_info:
            self.output.info("Test info message")
            mock_info.assert_called_once_with("Test info message")

    def test_success(self):
        """Test success output."""
        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output.logger, "info") as mock_info:
            self.output.success("Test success message")
            mock_info.assert_called_once_with("✅ Test success message")

    def test_warning(self):
        """Test warning output."""
        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output.logger, "warning") as mock_warning:
            self.output.warning("Test warning message")
            mock_warning.assert_called_once_with("⚠️  Test warning message")

    def test_error(self):
        """Test error output."""
        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output.logger, "error") as mock_error:
            self.output.error("Test error message")
            mock_error.assert_called_once_with("❌ Test error message")

    def test_debug(self):
        """Test debug output with verbose=False."""
        # Debug shouldn't output when verbose is False
        self.output.verbose = False
        with mock.patch.object(self.output, "rich_console") as mock_rich_console:
            with mock.patch.object(self.output.logger, "debug") as mock_debug:
                self.output.debug("Test debug message")
                mock_debug.assert_not_called()
                mock_rich_console.assert_not_called()

        # Debug should output when verbose is True
        self.output.verbose = True
        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output.logger, "debug") as mock_debug:
            self.output.debug("Test debug message")
            mock_debug.assert_called_once_with("Test debug message")

    def test_separator(self):
        """Test separator output."""
        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output.logger, "info") as mock_info:
            self.output.separator(length=10)
            mock_info.assert_called_once_with("==========")  # 10 equals signs

            mock_info.reset_mock()
            # Test with custom character
            self.output.separator(char="-", length=5)
            mock_info.assert_called_once_with("-----")  # 5 dashes

    def test_blank(self):
        """Test blank line output."""
        with mock.patch.object(self.output, "info") as mock_info:
            self.output.blank()
            mock_info.assert_called_once_with("")

    # The banner method doesn't exist in the Output class, removing this test
    # def test_banner(self):
    #    """Test banner output."""
    #    self.output.banner("Test Tool", "1.0.0", {"Key": "Value"})
    #    output = self.stdout_capture.getvalue()
    #    self.assertIn("Test Tool", output)
    #    self.assertIn("1.0.0", output)
    #    self.assertIn("Key", output)
    #    self.assertIn("Value", output)

    def test_simple_table(self):
        """Test simple table output."""
        headers = ["Name", "Value"]
        rows = [["Item 1", "100"], ["Item 2", "200"]]

        self.output.rich_console = None  # Use standard logger path
        with mock.patch.object(self.output, "info") as mock_info:
            self.output.print_table(headers, rows)
            # Verify info was called multiple times (for headers and rows)
            self.assertTrue(mock_info.call_count >= 3)

    @mock.patch("rich.console.Console")
    def test_rich_table(self, mock_console_class):
        """Test rich table output."""
        # Create a mock console
        mock_console = mock.MagicMock()
        mock_console_class.return_value = mock_console

        # Setup rich_console
        self.output.rich_console = mock_console

        headers = ["Name", "Value"]
        rows = [["Item 1", "100"], ["Item 2", "200"]]

        self.output.print_table(headers, rows)

        # Check that print was called on the rich console
        mock_console.print.assert_called_once()
        args, kwargs = mock_console.print.call_args
        # Check that a Table object was passed
        self.assertTrue(any("Table" in str(arg) for arg in args))

    def test_progress_bar_simple(self):
        """Test simple progress bar."""
        # We need to mock sys.stdout to properly test this
        original_stdout = sys.stdout
        try:
            # Use StringIO to capture output
            mock_stdout = StringIO()
            sys.stdout = mock_stdout

            with self.output.create_progress_bar(
                total=10, description="Testing"
            ) as progress:
                for i in range(5):
                    progress.update()

            output = mock_stdout.getvalue()
            self.assertTrue("Testing" in output or "%" in output)
        finally:
            sys.stdout = original_stdout

    @mock.patch("rich.progress.Progress")
    def test_progress_bar_rich(self, mock_progress_class):
        """Test rich progress bar."""
        # Create mock progress and task
        mock_progress = mock.MagicMock()
        mock_progress_class.return_value = mock_progress
        mock_task_id = 123
        mock_progress.add_task.return_value = mock_task_id

        # Setup rich_console to ensure rich is used
        self.output.rich_console = mock.MagicMock()
        self.output.rich_progress = mock_progress_class

        with self.output.create_progress_bar(
            total=10, description="Testing"
        ) as progress:
            progress.update()

        # Check progress was created and updated
        mock_progress.add_task.assert_called_once()
        mock_progress.update.assert_called_with(mock_task_id, advance=1)
        mock_progress.start.assert_called_once()
        mock_progress.stop.assert_called_once()


class TestSetupToolOutput(unittest.TestCase):
    """Tests for the setup_tool_output function."""

    def test_setup_basic(self):
        """Test basic setup."""
        output = setup_tool_output("test_tool")
        self.assertEqual(output.tool_name, "test_tool")
        self.assertFalse(output.verbose)
        self.assertEqual(output.logger.level, logging.INFO)

    def test_setup_log_level(self):
        """Test with custom log level."""
        output = setup_tool_output("test_tool", log_level="DEBUG")
        self.assertTrue(output.verbose)
        self.assertEqual(output.logger.level, logging.DEBUG)

    @mock.patch("os.makedirs")
    @mock.patch("os.path.expanduser")
    @mock.patch("logging.FileHandler")
    def test_setup_with_file_logging(
        self, mock_file_handler, mock_expanduser, mock_makedirs
    ):
        """Test setup with file logging."""
        mock_expanduser.return_value = "/mock/path"
        mock_handler = mock.MagicMock()
        mock_file_handler.return_value = mock_handler

        output = setup_tool_output("test_tool", log_to_file=True)

        # Check the file handler was added
        mock_file_handler.assert_called_once()
        self.assertTrue(
            any(handler == mock_handler for handler in output.logger.handlers)
        )

    @mock.patch("os.makedirs")
    @mock.patch("os.path.expanduser")
    @mock.patch("logging.FileHandler")
    def test_setup_with_output_dir(
        self, mock_file_handler, mock_expanduser, mock_makedirs
    ):
        """Test setup with custom output directory."""
        mock_expanduser.return_value = "/mock/output/dir"

        _ = setup_tool_output("test_tool", log_to_file=True, output_dir="~/logs")

        # Check that the directory was created
        mock_makedirs.assert_called_once_with("/mock/output/dir", exist_ok=True)
        mock_file_handler.assert_called_once()


class TestSimpleProgressBar(unittest.TestCase):
    """Tests for the SimpleProgressBar class."""

    def setUp(self):
        """Set up test fixtures."""
        # Capture stdout
        self.stdout_capture = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.stdout_capture

    def tearDown(self):
        """Tear down test fixtures."""
        sys.stdout = self.original_stdout

    def test_simple_progress_bar(self):
        """Test the simple progress bar."""
        with SimpleProgressBar(total=10, description="Testing") as progress:
            for i in range(5):
                progress.update()

        output = self.stdout_capture.getvalue()
        self.assertIn("Testing", output)
        self.assertIn("[", output)  # Check for progress bar
        self.assertIn("%", output)  # Check for percentage


class TestRichProgressAdapter(unittest.TestCase):
    """Tests for the RichProgressAdapter class."""

    def test_rich_progress_adapter(self):
        """Test the rich progress adapter."""
        mock_progress = mock.MagicMock()
        mock_task_id = 123

        with RichProgressAdapter(mock_progress, mock_task_id) as adapter:
            adapter.update()
            adapter.update(5)

        # Check that start, update, and stop were called
        mock_progress.start.assert_called_once()
        mock_progress.update.assert_any_call(mock_task_id, advance=1)
        mock_progress.update.assert_any_call(mock_task_id, advance=5)
        mock_progress.stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
