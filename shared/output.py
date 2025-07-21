#!/usr/bin/env python3
"""
Output handler for IntermCLI tools.
Provides consistent output formatting with optional rich enhancements.
"""
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Setup default logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class Output:
    def __init__(self, tool_name: str, use_rich: bool = True, verbose: bool = False):
        """
        Initialize output handler with optional rich support.

        Args:
            tool_name: Name of the tool
            use_rich: Whether to use rich formatting if available
            verbose: Whether to output verbose messages
        """
        self.tool_name = tool_name
        self.logger = logging.getLogger(tool_name)
        self.verbose = verbose

        # Check if we're in a terminal that supports color
        self.supports_color = self._supports_color()

        # Try to use rich if requested
        self.rich_console = None
        self.rich_progress = None
        self.rich_markdown = None
        if use_rich and self.supports_color:
            try:
                from rich.console import Console
                from rich.theme import Theme

                theme = Theme(
                    {
                        "info": "cyan",
                        "success": "green",
                        "warning": "yellow",
                        "error": "bold red",
                        "highlight": "bold cyan",
                        "muted": "dim",
                    }
                )

                self.rich_console = Console(theme=theme)

                # Import other rich components
                try:
                    from rich.progress import Progress

                    self.rich_progress = Progress
                except ImportError:
                    pass

                try:
                    from rich.markdown import Markdown

                    self.rich_markdown = Markdown
                except ImportError:
                    pass

            except ImportError:
                pass

    def _supports_color(self) -> bool:
        """
        Check if the terminal supports color output.

        Returns:
            True if color is supported, False otherwise
        """
        # Check if environment explicitly disables color
        if os.environ.get("NO_COLOR") is not None:
            return False

        # Check if we're in a terminal
        if not sys.stdout.isatty():
            return False

        # Check for known color-supporting terminals
        plat = sys.platform
        supported_platform = plat != "win32" or "ANSICON" in os.environ

        # Windows 10 supports ANSI escape sequences
        is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

        return supported_platform and is_a_tty

    def debug(self, message: str) -> None:
        """
        Print debug message (only if verbose is enabled).

        Args:
            message: Debug message to print
        """
        if not self.verbose:
            return

        if self.rich_console:
            self.rich_console.print(f"[muted][DEBUG] {message}[/muted]")
        else:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """
        Print info message with optional rich formatting.

        Args:
            message: Info message to print
        """
        if self.rich_console:
            self.rich_console.print(message)
        else:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        Print warning message with optional rich formatting.

        Args:
            message: Warning message to print
        """
        if self.rich_console:
            self.rich_console.print(f"[warning]⚠️  {message}[/warning]")
        else:
            self.logger.warning(f"⚠️  {message}")

    def error(self, message: str) -> None:
        """
        Print error message with optional rich formatting.

        Args:
            message: Error message to print
        """
        if self.rich_console:
            self.rich_console.print(f"[error]❌ {message}[/error]")
        else:
            self.logger.error(f"❌ {message}")

    def success(self, message: str) -> None:
        """
        Print success message with optional rich formatting.

        Args:
            message: Success message to print
        """
        if self.rich_console:
            self.rich_console.print(f"[success]✅ {message}[/success]")
        else:
            self.logger.info(f"✅ {message}")

    def highlight(self, message: str) -> None:
        """
        Print highlighted message with optional rich formatting.

        Args:
            message: Message to highlight
        """
        if self.rich_console:
            self.rich_console.print(f"[highlight]{message}[/highlight]")
        else:
            self.logger.info(message)

    def separator(self, char: str = "=", length: int = 60) -> None:
        """
        Print a separator line.

        Args:
            char: Character to use for separator
            length: Length of separator line
        """
        self.info(char * length)

    def blank(self) -> None:
        """Print a blank line."""
        self.info("")

    def print_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        """
        Print a table with optional rich formatting.

        Args:
            headers: List of column headers
            rows: List of rows, each a list of cell values
        """
        if self.rich_console:
            try:
                from rich.table import Table

                table = Table()
                for header in headers:
                    table.add_column(header)
                for row in rows:
                    table.add_row(*[str(cell) for cell in row])
                self.rich_console.print(table)
            except ImportError:
                self._print_simple_table(headers, rows)
        else:
            self._print_simple_table(headers, rows)

    def _print_simple_table(self, headers: List[str], rows: List[List[Any]]) -> None:
        """
        Print a simple ASCII table without rich.

        Args:
            headers: List of column headers
            rows: List of rows, each a list of cell values
        """
        if not rows:
            self.info("(No data)")
            return

        # Calculate column widths
        widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

        # Print headers
        header_row = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
        self.info(header_row)
        self.info("-" * len(header_row))

        # Print rows
        for row in rows:
            row_str = " | ".join(
                str(cell).ljust(widths[i])
                for i, cell in enumerate(row)
                if i < len(widths)
            )
            self.info(row_str)

    def create_progress_bar(self, total: int, description: str = "Processing") -> Any:
        """
        Create a progress bar with optional rich formatting.

        Args:
            total: Total number of items
            description: Progress bar description

        Returns:
            Progress bar object (use in a with statement)
        """
        if self.rich_console and self.rich_progress:
            # Import columns only when needed to avoid undefined names
            from rich.progress import BarColumn, TaskProgressColumn, TextColumn

            progress = self.rich_progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.rich_console,
            )
            task_id = progress.add_task(description, total=total)
            return RichProgressAdapter(progress, task_id)
        return SimpleProgressBar(total, description)

    def print_markdown(self, markdown_text: str) -> None:
        """
        Print markdown text with optional rich formatting.

        Args:
            markdown_text: Markdown text to print
        """
        if self.rich_console and self.rich_markdown:
            self.rich_console.print(self.rich_markdown(markdown_text))
        else:
            self.info(markdown_text)

    def print_json(self, data: Dict[str, Any], title: Optional[str] = None) -> None:
        """
        Print JSON data with optional rich formatting.

        Args:
            data: JSON data to print
            title: Optional title
        """
        if self.rich_console:
            try:
                import json

                from rich.syntax import Syntax

                json_str = json.dumps(data, indent=2)
                if title:
                    self.info(f"\n{title}:")
                self.rich_console.print(Syntax(json_str, "json"))
            except ImportError:
                import json

                if title:
                    self.info(f"\n{title}:")
                self.info(json.dumps(data, indent=2))
        else:
            import json

            if title:
                self.info(f"\n{title}:")
            self.info(json.dumps(data, indent=2))


class SimpleProgressBar:
    """A simple progress bar fallback when rich is not available."""

    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize simple progress bar.

        Args:
            total: Total number of items
            description: Progress bar description
        """
        self.total = total
        self.description = description
        self.current = 0
        self.bar_length = 40

    def update(self, n: int = 1) -> None:
        """
        Update the progress bar.

        Args:
            n: Number of steps to advance
        """
        self.current += n
        filled_length = int(self.bar_length * self.current / self.total)
        bar = "█" * filled_length + "-" * (self.bar_length - filled_length)
        percent = int(100 * self.current / self.total)
        sys.stdout.write(
            f"\r{self.description}: |{bar}| {percent}% ({self.current}/{self.total})"
        )
        sys.stdout.flush()
        if self.current >= self.total:
            sys.stdout.write("\n")

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.current < self.total:
            self.current = self.total
            self.update(0)


class RichProgressAdapter:
    """Adapter for rich progress to match the simple progress bar interface."""

    def __init__(self, progress: Any, task_id: Any):
        """
        Initialize rich progress adapter.

        Args:
            progress: Rich progress object
            task_id: Task ID from rich progress
        """
        self.progress = progress
        self.task_id = task_id

    def update(self, n: int = 1) -> None:
        """
        Update the progress bar.

        Args:
            n: Number of steps to advance
        """
        self.progress.update(self.task_id, advance=n)

    def __enter__(self):
        """Enter context manager."""
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.progress.stop()


def create_output(
    tool_name: str, use_rich: bool = True, verbose: bool = False
) -> Output:
    """
    Helper function to create an output handler.

    Args:
        tool_name: Name of the tool
        use_rich: Whether to use rich formatting if available
        verbose: Whether to output verbose messages

    Returns:
        Output handler
    """
    return Output(tool_name, use_rich, verbose)
