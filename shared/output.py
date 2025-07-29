#!/usr/bin/env python3
"""
Output handler for IntermCLI tools.
Provides consistent output formatting with optional rich enhancements.
"""
import logging
import os
import sys
from typing import Any, Dict, List, Optional


# Define progress bar adapter classes
class RichProgressAdapter:
    """Adapter for rich progress bars"""

    def __init__(self, progress: Any, task_id: Any) -> None:
        self.progress = progress
        self.task_id = task_id

    def __enter__(self) -> "RichProgressAdapter":
        self.progress.start()
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Any
    ) -> None:
        self.progress.stop()

    def update(self, advance: int = 1) -> None:
        self.progress.update(self.task_id, advance=advance)


class SimpleProgressBar:
    """Simple text-based progress bar for non-rich environments"""

    def __init__(self, total: int, description: str = "Processing") -> None:
        self.total = total
        self.current = 0
        self.description = description
        self.width = 30

    def __enter__(self) -> "SimpleProgressBar":
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Any
    ) -> None:
        sys.stdout.write("\n")
        sys.stdout.flush()

    def update(self, advance: int = 1) -> None:
        self.current += advance
        pct = min(100, int(100 * self.current / self.total))
        bar_length = int(self.width * self.current / self.total)
        bar = "[" + "#" * bar_length + " " * (self.width - bar_length) + "]"
        sys.stdout.write(f"\r{self.description} {bar} {pct}%")
        sys.stdout.flush()


class SimpleTableAdapter:
    """Simple table adapter for non-rich environments"""

    def __init__(
        self, title: Optional[str] = None, headers: Optional[List[str]] = None
    ) -> None:
        self.title = title
        self.headers = headers or []
        self.rows = []

    def add_row(self, *cells) -> None:
        """Add a row to the table"""
        self.rows.append([str(cell) for cell in cells])

    def add_column(self, header: str) -> None:
        """Add a column to the table"""
        self.headers.append(header)

    def __str__(self) -> str:
        """String representation of the table"""
        if not self.rows:
            return "(No data)"

        # Calculate column widths
        widths = [len(str(h)) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))

        lines = []

        # Add title if present
        if self.title:
            lines.append(self.title)
            lines.append("-" * len(self.title))

        # Add headers
        if self.headers:
            header_row = " | ".join(
                str(h).ljust(widths[i]) for i, h in enumerate(self.headers)
            )
            lines.append(header_row)
            lines.append("-" * len(header_row))

        # Add rows
        for row in self.rows:
            row_str = " | ".join(
                str(cell).ljust(widths[i])
                for i, cell in enumerate(row)
                if i < len(widths)
            )
            lines.append(row_str)

        return "\n".join(lines)


# Setup default logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def setup_tool_output(
    tool_name: str,
    log_level: str = "INFO",
    use_rich: bool = True,
    log_to_file: bool = False,
    log_file_path: str = "",
    output_dir: str = "",
) -> "Output":
    """
    Configure and return an Output instance with proper logging setup.

    Args:
        tool_name: Name of the tool (used for logger name and log file name)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_rich: Whether to use rich formatting if available
        log_to_file: Whether to also log to a file
        log_file_path: Specific path for the log file (optional)
        output_dir: Directory to store log files (if log_to_file is True)

    Returns:
        Configured Output instance ready for use
    """
    # Create output instance
    output = Output(
        tool_name, use_rich=use_rich, verbose=(log_level.upper() == "DEBUG")
    )

    # Set the logging level directly on the logger
    level = getattr(logging, log_level.upper(), logging.INFO)
    output.logger.setLevel(level)

    # Configure file logging if needed
    if log_to_file:
        if output_dir:
            output_dir_path = os.path.expanduser(output_dir)
            os.makedirs(output_dir_path, exist_ok=True)
            log_file = os.path.join(output_dir_path, f"{tool_name}.log")
        elif log_file_path:
            log_file = os.path.expanduser(log_file_path)
        else:
            log_file = os.path.expanduser(f"~/{tool_name}.log")

        # Add a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
        )
        output.logger.addHandler(file_handler)

    return output


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

    def print_table_obj(self, table: Any) -> None:
        """
        Print a table object created with create_table().

        Args:
            table: Table object (Rich Table or SimpleTableAdapter)
        """
        if isinstance(table, SimpleTableAdapter):
            self.info(str(table))
        elif self.rich_console:
            self.rich_console.print(table)
        else:
            # Fallback for unknown table type
            self.info(str(table))

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

    def create_table(
        self, title: Optional[str] = None, headers: Optional[List[str]] = None
    ) -> Any:
        """
        Create a table object that can be populated and then printed.

        Args:
            title: Optional title for the table
            headers: Optional list of column headers

        Returns:
            Table object that can be populated with add_row and then printed
        """
        if self.rich_console:
            try:
                from rich.table import Table

                table = Table(title=title)
                if headers:
                    for header in headers:
                        table.add_column(header)
                return table
            except ImportError:
                pass

        # Return a simple table adapter for non-rich environments
        return SimpleTableAdapter(title, headers)

    def print_list(
        self, items: List[str], numbered: bool = False, title: Optional[str] = None
    ) -> None:
        """
        Print a formatted list of items.

        Args:
            items: List of items to print
            numbered: Whether to use numbered list (True) or bullet points (False)
            title: Optional title for the list
        """
        if title:
            self.subheader(title)

        for i, item in enumerate(items, 1):
            prefix = f"{i}." if numbered else "•"
            self.info(f"{prefix} {item}")

    def status_update(self, message: str, status: str = "in_progress") -> None:
        """
        Show a status update with appropriate icon.

        Args:
            message: Status message to display
            status: Status type: "in_progress", "success", "warning", "error", or "info"
        """
        icons = {
            "in_progress": "🔄",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "info": "ℹ️",
        }
        icon = icons.get(status, "•")

        if self.rich_console:
            status_style = {
                "in_progress": "info",
                "success": "success",
                "warning": "warning",
                "error": "error",
                "info": "info",
            }.get(status, "info")

            self.rich_console.print(
                f"[{status_style}]{icon} {message}[/{status_style}]"
            )
        else:
            self.logger.info(f"{icon} {message}")

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

    def header(self, message: str) -> None:
        """
        Print a header/banner with optional rich formatting.

        Args:
            message: Header message to print
        """
        if self.rich_console:
            self.rich_console.print(f"\n[bold cyan]== {message} ==[/bold cyan]")
        else:
            self.logger.info(f"\n== {message} ==")

    def subheader(self, message: str) -> None:
        """
        Print a subheader with optional rich formatting.

        Args:
            message: Subheader message to print
        """
        if self.rich_console:
            self.rich_console.print(f"[bold]-- {message} --[/bold]")
        else:
            self.logger.info(f"-- {message} --")

    def task_start(self, task_name: str, details: str = "") -> None:
        """
        Print a task start message with optional rich formatting.

        Args:
            task_name: Name of the task
            details: Optional additional details
        """
        message = f"🔄 Starting {task_name}..."
        if details:
            message = f"{message} {details}"

        if self.rich_console:
            self.rich_console.print(f"[info]{message}[/info]")
        else:
            self.logger.info(message)

    def task_complete(self, task_name: str, details: str = "") -> None:
        """
        Print a task completion message with optional rich formatting.

        Args:
            task_name: Name of the task
            details: Optional additional details
        """
        message = f"✅ Completed {task_name}"
        if details:
            message = f"{message}: {details}"

        if self.rich_console:
            self.rich_console.print(f"[success]{message}[/success]")
        else:
            self.logger.info(message)

    def section(self, name: str) -> None:
        """
        Print a section header with optional rich formatting.

        Args:
            name: Section name
        """
        if self.rich_console:
            self.rich_console.print(f"\n[bold cyan]== {name} ==[/bold cyan]")
        else:
            self.logger.info(f"\n== {name} ==")

    def item(self, key: str, value: str) -> None:
        """
        Print a key-value item with optional rich formatting.

        Args:
            key: Item key
            value: Item value
        """
        if self.rich_console:
            self.rich_console.print(f"[bold]{key}:[/bold] {value}")
        else:
            self.logger.info(f"{key}: {value}")

    def banner(
        self, tool_name: str, version: str, details: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Print a standard tool banner with optional rich formatting.

        Args:
            tool_name: Name of the tool
            version: Tool version
            details: Optional dictionary of details to include
        """
        if self.rich_console:
            self.rich_console.print(f"[bold cyan]🔧 {tool_name} v{version}[/bold cyan]")
            if details:
                for key, value in details.items():
                    self.rich_console.print(f"[bold]{key}:[/bold] {value}")
        else:
            self.logger.info(f"🔧 {tool_name} v{version}")
            if details:
                for key, value in details.items():
                    self.logger.info(f"{key}: {value}")

        # Add a blank line after the banner
        self.blank()

    def print_grouped_data(
        self, data: Dict[str, List[str]], show_empty: bool = False
    ) -> None:
        """
        Print grouped data with sections.

        Args:
            data: Dictionary mapping section names to lists of items
            show_empty: Whether to show empty sections
        """
        for section, items in data.items():
            if not items and not show_empty:
                continue

            self.subheader(section)

            if items:
                for item in items:
                    self.info(f"  • {item}")
            else:
                self.info("  (No items)")

            self.blank()

    def print_key_value_section(self, title: str, data: Dict[str, str]) -> None:
        """
        Print a section with key-value pairs.

        Args:
            title: Section title
            data: Dictionary of key-value pairs to display
        """
        self.subheader(title)

        if not data:
            self.info("  (No data)")
            return

        # Calculate max key length for alignment
        max_key_len = max(len(key) for key in data.keys())

        for key, value in data.items():
            aligned_key = key.ljust(max_key_len)
            if self.rich_console:
                self.rich_console.print(f"  [bold]{aligned_key}:[/bold] {value}")
            else:
                self.logger.info(f"  {aligned_key}: {value}")

        self.blank()
