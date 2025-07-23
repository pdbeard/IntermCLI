#!/usr/bin/env python3
"""
sort-files: Organize and declutter directories by automatically sorting files into subfolders
based on file type, date, size, or user-defined custom rules.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    sort-files ~/Downloads
    sort-files --by date ~/Documents
    sort-files --dry-run --show-skipped ~/Desktop
    sort-files --config ~/.config/intermcli/sort-files.toml ~/Downloads
"""

import fnmatch
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure shared utilities are available
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    from shared.path_utils import require_shared_utilities

    require_shared_utilities()
except ImportError:
    # If even path_utils can't be imported, provide a fallback error
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

from shared.arg_parser import ArgumentParser

# Import shared utilities
from shared.config_loader import ConfigLoader
from shared.enhancement_loader import EnhancementLoader
from shared.output import Output

# Version
__version__ = "0.1.0"
TOOL_NAME = "sort-files"


# --- Config loading ---
def load_config(config_path=None) -> Dict[str, Any]:
    """
    Load TOML config using the shared ConfigLoader utility.
    Args:
        config_path (str or Path, optional): Path to a config file. If not provided, tries user and source-tree defaults.
    Returns:
        dict: Configuration dictionary for sorting rules and options.
    """
    # Use the shared ConfigLoader
    config_loader = ConfigLoader(TOOL_NAME)
    # Add the specific config file if provided
    if config_path:
        config_loader.add_config_file(config_path)
    # Load the configuration with proper precedence
    config = config_loader.load_config()
    return config


# --- Core logic ---
def get_file_type(file: Path, type_folders: Dict[str, List[str]]) -> str:
    """
    Determine the file type category for a given file based on its extension.
    Args:
        file (Path): The file to categorize.
        type_folders (dict): Mapping of folder names to lists of extensions.
    Returns:
        str: The folder/category name, or 'other' if no match.
    """
    ext = file.suffix.lower()
    for folder, exts in type_folders.items():
        if not isinstance(exts, list):
            continue
        if ext in exts:
            return folder
    return "other"


def match_custom_rule(filename: str, custom_rules: Dict[str, str]) -> Optional[str]:
    """
    Return the folder name if filename matches a custom rule pattern.
    Args:
        filename (str): The filename to check.
        custom_rules (dict): Mapping of glob patterns to folder names.
    Returns:
        str or None: The folder name if matched, else None.
    """
    for pattern, folder in custom_rules.items():
        if fnmatch.fnmatch(filename, pattern):
            return folder
    return None


def handle_file_operation_error(
    entry: Path, exception: Exception, output: Output
) -> Tuple[str, str]:
    """
    Handle errors when moving files and return appropriate messages and skip reason.

    Args:
        entry: The file that was being moved
        exception: The exception that was raised
        output: Output utility for displaying messages

    Returns:
        Tuple containing (error_message, skip_reason)
    """
    if isinstance(exception, PermissionError):
        msg = f"Failed to move {entry.name}: Permission denied. Try running with elevated permissions."
        reason = "permission denied"
    elif isinstance(exception, FileNotFoundError):
        msg = f"Failed to move {entry.name}: File not found. It may have been moved or deleted."
        reason = "file not found"
    else:
        msg = f"Failed to move {entry.name}: {exception}"
        reason = f"error: {exception}"

    output.error(msg)
    return msg, reason


def sort_files(
    target_dir: Path,
    rules: Dict[str, Any],
    type_folders: Dict[str, List[str]],
    dry_run: bool = False,
    safe: bool = True,
    skip_hidden: bool = True,
    skip_dirs: List[str] = None,
    output: Output = None,
) -> Tuple[List[Tuple[Path, Path]], List[Tuple[Path, str]]]:
    """
    Sort files in a directory according to rules and type folders.
    Args:
        target_dir (Path): Directory to organize.
        rules (dict): Sorting rules (by_type, by_date, by_size, custom).
        type_folders (dict): Mapping of folder names to extensions.
        dry_run (bool): If True, only log actions without moving files.
        safe (bool): If True, skip files that would overwrite existing ones.
        skip_hidden (bool): If True, skip hidden files and folders.
        skip_dirs (list): List of directory names to skip.
        output: Output utility for display
    Returns:
        tuple: (moved, skipped) lists of (entry, dest_dir) and (entry, reason).
    """
    moved = []
    skipped = []
    skip_dirs = skip_dirs or []
    entries = list(target_dir.iterdir())
    total_files = sum(
        1
        for entry in entries
        if entry.is_file() and not (skip_hidden and entry.name.startswith("."))
    )
    output.info(f"Processing {total_files} files in {target_dir}...")
    for entry in entries:
        if entry.is_dir():
            if entry.name in skip_dirs or (skip_hidden and entry.name.startswith(".")):
                continue
            # Don't recurse for now (could add --recursive)
            continue
        if skip_hidden and entry.name.startswith("."):
            continue

        # --- Custom rules first ---
        custom_rules = rules.get("custom", {})
        custom_folder = match_custom_rule(entry.name, custom_rules)
        if custom_folder:
            dest_dir = target_dir / custom_folder
        # --- By type ---
        elif rules.get("by_type", True):
            folder = get_file_type(entry, type_folders)
            dest_dir = target_dir / folder
        # --- By date ---
        elif rules.get("by_date", False):
            mtime = datetime.fromtimestamp(entry.stat().st_mtime)
            folder = mtime.strftime("%Y-%m")
            dest_dir = target_dir / folder
        # --- By size ---
        elif rules.get("by_size", False):
            size = entry.stat().st_size
            if size > 1024 * 1024 * 100:
                folder = "huge"
            elif size > 1024 * 1024 * 10:
                folder = "large"
            elif size > 1024 * 1024:
                folder = "medium"
            else:
                folder = "small"
            dest_dir = target_dir / folder
        else:
            dest_dir = target_dir / "other"

        dest = dest_dir / entry.name
        if safe and dest.exists():
            skipped.append((entry, "exists"))
            continue

        if dry_run:
            msg = f"Would move: {entry.name} → {dest_dir.name}/"
            output.info(msg)
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(entry), str(dest))
                moved.append((entry, dest_dir))
            except Exception as e:
                _, reason = handle_file_operation_error(entry, e, output)
                skipped.append((entry, reason))
    return moved, skipped


# --- Dependency checking ---
def check_dependencies():
    """Check status of optional dependencies"""
    enhancer = EnhancementLoader(TOOL_NAME)
    enhancer.check_dependency("rich", "Rich output formatting")
    enhancer.check_dependency("tomllib", "TOML configuration support")
    enhancer.check_dependency("tomli", "TOML support for Python < 3.11")
    enhancer.print_status()


# --- CLI ---
def main():
    """
    CLI entry point for sort-files. Parses arguments, loads config, and runs sorting logic.
    Uses shared utilities for configuration, output, and enhancement detection.
    """
    # Use the shared ArgumentParser
    arg_parser = ArgumentParser(
        tool_name=TOOL_NAME,
        description="Organize files in a directory by type, date, size, or custom rules.",
        epilog="Example: sort-files --by type ~/Downloads",
        version=__version__,
    )

    # Add tool-specific arguments
    arg_parser.parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to organize (default: current)",
    )
    arg_parser.parser.add_argument(
        "--by",
        choices=["type", "date", "size"],
        default="type",
        help="How to organize files (default: type)",
    )
    arg_parser.parser.add_argument("--config", help="Path to configuration file")
    arg_parser.parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done, without moving files",
    )
    arg_parser.parser.add_argument(
        "--unsafe", action="store_true", help="Allow overwriting files in destination"
    )
    arg_parser.parser.add_argument(
        "--show-skipped", action="store_true", help="Show skipped files"
    )
    arg_parser.parser.add_argument(
        "--check-deps", action="store_true", help="Check optional dependency status"
    )

    args = arg_parser.parser.parse_args()

    # Check dependencies if requested
    if args.check_deps:
        check_dependencies()
        return

    # Initialize output handling using shared Output
    output = Output(TOOL_NAME, verbose=False)

    # Load configuration
    config = load_config(args.config)

    # Override with command line arguments
    config["rules"] = {
        "by_type": args.by == "type",
        "by_date": args.by == "date",
        "by_size": args.by == "size",
        "custom": config.get("rules", {}).get("custom", {}),
    }
    config["dry_run"] = args.dry_run
    config["safe"] = not args.unsafe

    target_dir = Path(args.directory).expanduser().resolve()
    if not target_dir.exists() or not target_dir.is_dir():
        output.error(f"Directory does not exist: {target_dir}")
        sys.exit(1)

    # Determine rule type
    if config["rules"]["by_type"]:
        rule = "type"
    elif config["rules"]["by_date"]:
        rule = "date"
    elif config["rules"]["by_size"]:
        rule = "size"
    else:
        rule = "custom/other"

    # Header display
    output.banner(
        TOOL_NAME,
        __version__,
        {
            "Target": str(target_dir),
            "Rule": rule,
            "Dry run": "ON" if config["dry_run"] else "OFF",
        },
    )

    # Count the files that will be processed
    entries = list(target_dir.iterdir())
    total_files = sum(
        1
        for entry in entries
        if entry.is_file()
        and not (config.get("skip_hidden", True) and entry.name.startswith("."))
    )

    # Start sorting task
    output.task_start("Sorting files", f"{total_files} files in {target_dir}")

    moved, skipped = sort_files(
        target_dir,
        config["rules"],
        config["type_folders"],
        dry_run=config["dry_run"],
        safe=config["safe"],
        skip_hidden=config.get("skip_hidden", True),
        skip_dirs=config.get("skip_dirs", []),
        output=output,
    )

    # --- Summary Table ---
    folder_counts = Counter()
    for entry, dest_dir in moved:
        folder_counts[str(dest_dir.name)] += 1

    # Complete sorting task
    output.task_complete("Sorting files", f"{len(moved)} files moved")

    if folder_counts:
        output.header("Summary")
        if output.rich_console:
            table = output.create_table(
                title="Files by Category", headers=["Folder", "Files"]
            )
            for folder, count in sorted(folder_counts.items()):
                table.add_row(folder, str(count))
            output.print_table(table)
        else:
            for folder, count in sorted(folder_counts.items()):
                output.item(folder, f"{count} file{'s' if count != 1 else ''}")

    if (args.show_skipped or config["dry_run"]) and skipped:
        output.subheader("Skipped Files")
        for entry, reason in skipped:
            output.warning(f"{entry.name}: {reason}")


if __name__ == "__main__":
    main()
