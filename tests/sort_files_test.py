import importlib.util
import os
import sys
from datetime import datetime

# Rich/Console import and availability check for test output capture
from io import StringIO
from pathlib import Path

import pytest

try:
    from rich.console import Console

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Dynamically import the sort-files tool as a module
TOOL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
)
spec = importlib.util.spec_from_file_location("sort_files", TOOL_PATH)
sort_files = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sort_files)


def test_get_file_type_basic():
    type_folders = sort_files.load_config()["type_folders"]
    file = Path("foo.jpg")
    assert sort_files.get_file_type(file, type_folders) == "images"
    file = Path("bar.pdf")
    assert sort_files.get_file_type(file, type_folders) == "documents"
    file = Path("baz.unknown")
    assert sort_files.get_file_type(file, type_folders) == "other"


def test_match_custom_rule():
    custom_rules = {"*-receipt.pdf": "Receipts", "*.log": "Logs"}
    assert sort_files.match_custom_rule("2024-receipt.pdf", custom_rules) == "Receipts"
    assert sort_files.match_custom_rule("error.log", custom_rules) == "Logs"
    assert sort_files.match_custom_rule("foo.txt", custom_rules) is None


def test_sort_files_by_type(tmp_path):
    # Create files of different types
    img = tmp_path / "test.jpg"
    doc = tmp_path / "test.pdf"
    other = tmp_path / "test.unknown"
    img.write_bytes(b"img")
    doc.write_bytes(b"doc")
    other.write_bytes(b"other")
    rules = {"by_type": True, "by_date": False, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(
        tmp_path, rules, type_folders, dry_run=False, safe=True
    )
    # Check files moved
    assert (tmp_path / "images" / "test.jpg").exists()
    assert (tmp_path / "documents" / "test.pdf").exists()
    assert (tmp_path / "other" / "test.unknown").exists()


def test_sort_files_dry_run(tmp_path, capsys):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"img")
    rules = {"by_type": True, "by_date": False, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    if HAS_RICH:
        buf = StringIO()
        console = Console(file=buf, force_terminal=True, color_system=None)
        moved, skipped = sort_files.sort_files(
            tmp_path, rules, type_folders, dry_run=True, safe=True, console=console
        )
        output = buf.getvalue()
    else:
        # fallback: capture logging output via capsys
        moved, skipped = sort_files.sort_files(
            tmp_path, rules, type_folders, dry_run=True, safe=True, console=None
        )
        output = capsys.readouterr().out
    assert "[DRY RUN] Would move: test.jpg" in output
    assert not (tmp_path / "images" / "test.jpg").exists()


def test_sort_files_safe(tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"img")
    dest_dir = tmp_path / "images"
    dest_dir.mkdir()
    dest_file = dest_dir / "test.jpg"
    dest_file.write_bytes(b"existing")
    rules = {"by_type": True, "by_date": False, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(
        tmp_path, rules, type_folders, dry_run=False, safe=True
    )
    # Should skip moving since file exists
    assert (tmp_path / "images" / "test.jpg").read_bytes() == b"existing"
    assert any(reason == "exists" for _, reason in skipped)


def test_sort_files_unsafe(tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"img")
    dest_dir = tmp_path / "images"
    dest_dir.mkdir()
    dest_file = dest_dir / "test.jpg"
    dest_file.write_bytes(b"existing")
    rules = {"by_type": True, "by_date": False, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(
        tmp_path, rules, type_folders, dry_run=False, safe=False
    )
    # Should overwrite file
    assert (tmp_path / "images" / "test.jpg").read_bytes() == b"img"


def test_sort_files_custom_rule(tmp_path):
    receipt = tmp_path / "2024-receipt.pdf"
    receipt.write_bytes(b"receipt")
    rules = {
        "by_type": True,
        "by_date": False,
        "by_size": False,
        "custom": {"*-receipt.pdf": "Receipts"},
    }
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(
        tmp_path, rules, type_folders, dry_run=False, safe=True
    )
    assert (tmp_path / "Receipts" / "2024-receipt.pdf").exists()


def test_sort_files_by_date(tmp_path):
    file = tmp_path / "old.txt"
    file.write_bytes(b"old")
    # Set mtime to Jan 2022
    old_time = datetime(2022, 1, 1).timestamp()
    os.utime(file, (old_time, old_time))
    rules = {"by_type": False, "by_date": True, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(
        tmp_path, rules, type_folders, dry_run=False, safe=True
    )
    assert (tmp_path / "2022-01" / "old.txt").exists()


def test_sort_files_by_size(tmp_path):
    small = tmp_path / "small.txt"
    medium = tmp_path / "medium.txt"
    large = tmp_path / "large.txt"
    huge = tmp_path / "huge.txt"
    small.write_bytes(b"a" * 100)
    medium.write_bytes(b"a" * (1024 * 1024 + 1))
    large.write_bytes(b"a" * (1024 * 1024 * 11))
    huge.write_bytes(b"a" * (1024 * 1024 * 101))
    rules = {"by_type": False, "by_date": False, "by_size": True, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(
        tmp_path, rules, type_folders, dry_run=False, safe=True
    )
    assert (tmp_path / "small" / "small.txt").exists()
    assert (tmp_path / "medium" / "medium.txt").exists()
    assert (tmp_path / "large" / "large.txt").exists()
    assert (tmp_path / "huge" / "huge.txt").exists()


def test_main_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["sort-files.py", "--help"])
    with pytest.raises(SystemExit):
        sort_files.main()
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_no_rich(monkeypatch):
    """Test fallback when Rich is not installed."""
    import importlib
    import sys

    # Remove rich from sys.modules and reload
    sys_modules_backup = sys.modules.copy()
    sys.modules["rich"] = None
    sys.modules["rich.console"] = None
    sys.modules["rich.table"] = None
    sys.modules["rich.theme"] = None
    import importlib.util

    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
    )
    spec = importlib.util.spec_from_file_location("sort_files_no_rich", TOOL_PATH)
    sort_files_no_rich = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sort_files_no_rich)
    assert not sort_files_no_rich.HAS_RICH
    assert sort_files_no_rich.console is None
    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_no_toml(monkeypatch, caplog):
    """Test fallback when neither tomllib nor tomli is available."""
    import importlib
    import sys

    sys_modules_backup = sys.modules.copy()
    sys.modules["tomllib"] = None
    sys.modules["tomli"] = None
    import importlib.util

    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
    )
    spec = importlib.util.spec_from_file_location("sort_files_no_toml", TOOL_PATH)
    sort_files_no_toml = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sort_files_no_toml)
    with caplog.at_level("WARNING"):
        config = sort_files_no_toml.load_config()
        assert "TOML support not available" in caplog.text
        assert isinstance(config, dict)
    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_config_path_logic(tmp_path):
    """Test that a custom config path is used if provided."""
    config_file = tmp_path / "custom.toml"
    config_file.write_text(
        """
[rules]
by_type = false
by_date = true
by_size = false
"""
    )
    import importlib.util

    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
    )
    spec = importlib.util.spec_from_file_location("sort_files_config_path", TOOL_PATH)
    sort_files_config_path = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sort_files_config_path)
    config = sort_files_config_path.load_config(str(config_file))
    assert config["rules"]["by_date"] is True
    assert config["rules"]["by_type"] is False


def test_permission_and_file_not_found(monkeypatch, tmp_path):
    """Test PermissionError and FileNotFoundError branches in sort_files."""
    file = tmp_path / "file.txt"
    file.write_bytes(b"data")
    dest_dir = tmp_path / "docs"
    dest_dir.mkdir()
    # Patch shutil.move to raise PermissionError, then FileNotFoundError
    import importlib.util

    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
    )
    spec = importlib.util.spec_from_file_location("sort_files_perm", TOOL_PATH)
    sort_files_perm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sort_files_perm)

    def raise_perm(*a, **kw):
        raise PermissionError()

    def raise_notfound(*a, **kw):
        raise FileNotFoundError()

    # PermissionError
    monkeypatch.setattr(sort_files_perm.shutil, "move", raise_perm)
    moved, skipped = sort_files_perm.sort_files(
        tmp_path,
        {"by_type": True, "custom": {}},
        sort_files_perm.load_config()["type_folders"],
        dry_run=False,
        safe=False,
    )
    assert skipped and "permission denied" in skipped[0][1]
    # FileNotFoundError
    monkeypatch.setattr(sort_files_perm.shutil, "move", raise_notfound)
    moved, skipped = sort_files_perm.sort_files(
        tmp_path,
        {"by_type": True, "custom": {}},
        sort_files_perm.load_config()["type_folders"],
        dry_run=False,
        safe=False,
    )
    assert skipped and "file not found" in skipped[0][1]


def test_cli_directory_not_exist(monkeypatch, capsys):
    """Test CLI error for non-existent directory."""
    import importlib.util

    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
    )
    spec = importlib.util.spec_from_file_location("sort_files_cli", TOOL_PATH)
    sort_files_cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sort_files_cli)
    monkeypatch.setattr(sys, "argv", ["sort-files.py", "/no/such/dir"])
    with pytest.raises(SystemExit):
        sort_files_cli.main()
    out = capsys.readouterr().out
    assert (
        "Directory does not exist" in out
        or "Directory does not exist" in capsys.readouterr().err
    )


def test_cli_summary_and_show_skipped(tmp_path, capsys):
    """Test CLI summary output and --show-skipped option."""
    import importlib.util

    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/sort-files/sort-files.py")
    )
    spec = importlib.util.spec_from_file_location("sort_files_cli2", TOOL_PATH)
    sort_files_cli2 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sort_files_cli2)
    # Create a file and a conflicting file to trigger skipped
    file = tmp_path / "foo.txt"
    file.write_bytes(b"foo")
    dest_dir = tmp_path / "documents"
    dest_dir.mkdir()
    dest_file = dest_dir / "foo.txt"
    dest_file.write_bytes(b"bar")
    # Run CLI with --show-skipped
    import sys

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(sys, "argv", ["sort-files.py", str(tmp_path), "--show-skipped"])
    sort_files_cli2.main()
    out = capsys.readouterr().out
    assert "Skipped files" in out
    monkeypatch.undo()
