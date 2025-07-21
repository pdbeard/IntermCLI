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


import argparse
import fnmatch
import logging
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# Optional rich support
try:
    from rich.console import Console
    from rich.table import Table
    from rich.theme import Theme

    HAS_RICH = True
    console = Console(
        theme=Theme(
            {
                "info": "cyan",
                "success": "green",
                "warning": "yellow",
                "error": "bold red",
            }
        )
    )
except ImportError:
    HAS_RICH = False
    console = None


# TOML support with fallback
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # fallback for older Python
    except ImportError:
        tomllib = None

__version__ = "0.1.0"


# --- Config loading ---
def load_config(config_path=None):
    """
    Load TOML config with robust fallback (user, legacy, source-tree), else return defaults.
    Args:
        config_path (str or Path, optional): Path to a config file. If not provided, tries user and source-tree defaults.
    Returns:
        dict: Configuration dictionary for sorting rules and options.
    """
    config = {
        "rules": {"by_type": True, "by_date": False, "by_size": False, "custom": {}},
        "type_folders": {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
            "documents": [
                ".pdf",
                ".docx",
                ".doc",
                ".txt",
                ".md",
                ".odt",
                ".rtf",
                ".xls",
                ".xlsx",
                ".csv",
            ],
            "archives": [".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"],
            "audio": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
            "video": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm"],
            "code": [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".c",
                ".cpp",
                ".go",
                ".rb",
                ".php",
                ".sh",
                ".rs",
            ],
        },
        "dry_run": False,
        "safe": True,
        "skip_hidden": True,
        "skip_dirs": [],
    }
    script_dir = Path(__file__).parent
    source_config_file = script_dir / "config" / "defaults.toml"
    user_config_dir = Path.home() / ".config" / "intermcli"
    user_config_file = user_config_dir / "sort-files.toml"
    legacy_user_config_file = user_config_dir / "config.toml"

    config_loaded = None
    config_paths = []
    if config_path:
        config_paths.append(config_path)
    config_paths.extend(
        [
            str(user_config_file),
            str(legacy_user_config_file),
            str(source_config_file),
        ]
    )

    if not tomllib:
        logging.warning("TOML support not available")
        logging.info("Install tomli for Python < 3.11: pip3 install tomli")
        logging.info("Using built-in defaults")
        return config

    for path in config_paths:
        p = Path(path)
        if p.exists():
            try:
                with open(p, "rb") as f:
                    file_config = tomllib.load(f)
                    # Merge nested sections if present
                    if "rules" in file_config:
                        config["rules"].update(file_config["rules"])
                    if "type_folders" in file_config:
                        config["type_folders"].update(file_config["type_folders"])
                    # Top-level options
                    for key in ("dry_run", "safe", "skip_hidden", "skip_dirs"):
                        if key in file_config:
                            config[key] = file_config[key]
                config_loaded = str(p)
            except Exception as e:
                logging.warning(f"Could not load config: {path}: {e}")
            break  # Use the first config found

    if config_loaded:
        logging.info(f"Loaded config: {config_loaded}")
    else:
        logging.info("Using built-in defaults (no config file found)")
    return config


# --- Core logic ---
def get_file_type(file: Path, type_folders: dict) -> str:
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


def match_custom_rule(filename: str, custom_rules: dict) -> str | None:
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


def sort_files(
    target_dir: Path,
    rules: dict,
    type_folders: dict,
    dry_run: bool = False,
    safe: bool = True,
    skip_hidden: bool = True,
    skip_dirs: list = [],
    console=None,
) -> tuple[list, list]:
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
    Returns:
        tuple: (moved, skipped) lists of (entry, dest_dir) and (entry, reason).
    """
    moved = []
    skipped = []
    entries = list(target_dir.iterdir())
    total_files = sum(
        1
        for entry in entries
        if entry.is_file() and not (skip_hidden and entry.name.startswith("."))
    )
    if console:
        console.print(f"[info]Processing {total_files} files in {target_dir}...")
    else:
        logging.info(f"Processing {total_files} files in {target_dir}...")

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
            msg = f"[DRY RUN] Would move: {entry.name} → {dest_dir}/"
            if console:
                console.print(msg)
            else:
                logging.info(msg)
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(entry), str(dest))
                msg = f"Moved: {entry.name} → {dest_dir}/"
                if console:
                    console.print(msg)
                else:
                    logging.info(msg)
                moved.append((entry, dest_dir))
            except PermissionError:
                msg = f"Failed to move {entry.name}: Permission denied. Try running with elevated permissions."
                if console:
                    console.print(f"[error]{msg}[/error]")
                else:
                    logging.error(msg)
                skipped.append((entry, "permission denied"))
            except FileNotFoundError:
                msg = f"Failed to move {entry.name}: File not found. It may have been moved or deleted."
                if console:
                    console.print(f"[error]{msg}[/error]")
                else:
                    logging.error(msg)
                skipped.append((entry, "file not found"))
            except Exception as e:
                msg = f"Failed to move {entry.name}: {e}"
                if console:
                    console.print(f"[error]{msg}[/error]")
                else:
                    logging.error(msg)
                skipped.append((entry, f"error: {e}"))
    return moved, skipped


# --- CLI ---
def main():
    """
    CLI entry point for sort-files. Parses arguments, loads config, and runs sorting logic.
    Uses rich for output if available, otherwise falls back to logging.
    """
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by type, date, size, or custom rules.",
        epilog="Example: sort-files --by type ~/Downloads",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to organize (default: current)",
    )
    parser.add_argument(
        "--by",
        choices=["type", "date", "size"],
        default="type",
        help="Sort files by this rule",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved, but don't move files",
    )
    parser.add_argument("--config", help="Path to TOML config file")
    parser.add_argument(
        "--unsafe", action="store_true", help="Allow overwriting files in destination"
    )
    parser.add_argument(
        "--show-skipped", action="store_true", help="Show skipped files"
    )
    parser.add_argument(
        "--version", action="version", version=f"sort-files {__version__}"
    )

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    config = load_config(args.config)
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
        if HAS_RICH:
            console.print(f"[error]Directory does not exist: {target_dir}[/error]")
        else:
            logging.error(f"Directory does not exist: {target_dir}")
        sys.exit(1)

    # Header
    if HAS_RICH:
        console.print(f"[info]🗃️  sort-files {__version__}")
        console.print(f"[info]Target:[/] {target_dir}")
        if config["rules"]["by_type"]:
            rule = "type"
        elif config["rules"]["by_date"]:
            rule = "date"
        elif config["rules"]["by_size"]:
            rule = "size"
        else:
            rule = "custom/other"
        console.print(f"[info]Rule:[/] {rule}")
        console.print(f"[info]Dry run:[/] {'ON' if config['dry_run'] else 'OFF'}\n")
    else:
        logging.info(f"🗃️  sort-files {__version__}")
        logging.info(f"Target: {target_dir}")
        if config["rules"]["by_type"]:
            rule = "type"
        elif config["rules"]["by_date"]:
            rule = "date"
        elif config["rules"]["by_size"]:
            rule = "size"
        else:
            rule = "custom/other"
        logging.info(f"Rule: {rule}")
        logging.info(f"Dry run: {'ON' if config['dry_run'] else 'OFF'}\n")

    moved, skipped = sort_files(
        target_dir,
        config["rules"],
        config["type_folders"],
        dry_run=config["dry_run"],
        safe=config["safe"],
        skip_hidden=config.get("skip_hidden", True),
        skip_dirs=config.get("skip_dirs", []),
        console=console if HAS_RICH else None,
    )

    # --- Summary Table ---
    folder_counts = Counter()
    for entry, dest_dir in moved:
        folder_counts[str(dest_dir.name)] += 1

    if HAS_RICH:
        console.print(f"\n[success]✅ Done. {len(moved)} files moved.")
        if folder_counts:
            table = Table(
                title="Summary", show_header=True, header_style="bold magenta"
            )
            table.add_column("Folder", style="cyan")
            table.add_column("Files", style="green")
            for folder, count in sorted(folder_counts.items()):
                table.add_row(folder, str(count))
            console.print(table)
        if (args.show_skipped or config["dry_run"]) and skipped:
            console.print("\n[warning]Skipped files:")
            for entry, reason in skipped:
                console.print(f"  [yellow]{entry.name}[/yellow]: {reason}")
    else:
        logging.info(f"\n✅ Done. {len(moved)} files moved.")
        if folder_counts:
            logging.info("\nSummary:")
            for folder, count in sorted(folder_counts.items()):
                logging.info(f"  {folder:<15}: {count} file{'s' if count != 1 else ''}")
        if (args.show_skipped or config["dry_run"]) and skipped:
            logging.info("\nSkipped files:")
            for entry, reason in skipped:
                logging.info(f"  {entry.name}: {reason}")


if __name__ == "__main__":
    main()
