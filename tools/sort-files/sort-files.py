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
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

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
    """Load TOML config with robust fallback (user, legacy, source-tree), else return defaults."""
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
        print("⚠️  TOML support not available")
        print("💡 Install tomli for Python < 3.11: pip3 install tomli")
        print("💡 Using built-in defaults")
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
                print(f"⚠️  Could not load config: {path}: {e}")
            break  # Use the first config found

    if config_loaded:
        print(f"ℹ️  Loaded config: {config_loaded}")
    else:
        print("ℹ️  Using built-in defaults (no config file found)")
    return config


# --- Core logic ---
def get_file_type(file: Path, type_folders: dict):
    ext = file.suffix.lower()
    for folder, exts in type_folders.items():
        if not isinstance(exts, list):
            continue
        if ext in exts:
            return folder
    return "other"


def match_custom_rule(filename, custom_rules):
    """Return the folder name if filename matches a custom rule pattern."""
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
):
    moved = []
    skipped = []
    entries = list(target_dir.iterdir())
    total_files = sum(
        1
        for entry in entries
        if entry.is_file() and not (skip_hidden and entry.name.startswith("."))
    )
    print(f"Processing {total_files} files...")

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
            print(f"[DRY RUN] Would move: {entry.name} → {dest_dir}/")
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(entry), str(dest))
                print(f"Moved: {entry.name} → {dest_dir}/")
                moved.append((entry, dest_dir))
            except PermissionError:
                print(
                    "❌ Failed to move {}: Permission denied. Try running with elevated permissions.".format(
                        entry.name
                    )
                )
                skipped.append((entry, "permission denied"))
            except FileNotFoundError:
                print(
                    "❌ Failed to move {}: File not found. It may have been moved or deleted.".format(
                        entry.name
                    )
                )
                skipped.append((entry, "file not found"))
            except Exception as e:
                print(f"❌ Failed to move {entry.name}: {e}")
                skipped.append((entry, f"error: {e}"))
    return moved, skipped


# --- CLI ---
def main():
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
        print(f"❌ Directory does not exist: {target_dir}")
        sys.exit(1)

    print(f"🗃️  sort-files {__version__}")
    print(f"Target: {target_dir}")
    if config["rules"]["by_type"]:
        rule = "type"
    elif config["rules"]["by_date"]:
        rule = "date"
    elif config["rules"]["by_size"]:
        rule = "size"
    else:
        rule = "custom/other"
    print(f"Rule: {rule}")
    print(f"Dry run: {'ON' if config['dry_run'] else 'OFF'}")
    print("")

    moved, skipped = sort_files(
        target_dir,
        config["rules"],
        config["type_folders"],
        dry_run=config["dry_run"],
        safe=config["safe"],
        skip_hidden=config.get("skip_hidden", True),
        skip_dirs=config.get("skip_dirs", []),
    )

    # --- Summary Table ---

    folder_counts = Counter()
    for entry, dest_dir in moved:
        folder_counts[str(dest_dir.name)] += 1

    print(f"\n✅ Done. {len(moved)} files moved.")
    if folder_counts:
        print("\nSummary:")
        for folder, count in sorted(folder_counts.items()):
            print(f"  {folder:<15}: {count} file{'s' if count != 1 else ''}")

    if (args.show_skipped or config["dry_run"]) and skipped:
        print("\nSkipped files:")
        for entry, reason in skipped:
            print(f"  {entry.name}: {reason}")


if __name__ == "__main__":
    main()
