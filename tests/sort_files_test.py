
import sys
import os
import pytest
import importlib.util
from pathlib import Path
from datetime import datetime

# Dynamically import the sort-files tool as a module
TOOL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools/sort-files/sort-files.py'))
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
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=False, safe=True)
    # Check files moved
    assert (tmp_path / "images" / "test.jpg").exists()
    assert (tmp_path / "documents" / "test.pdf").exists()
    assert (tmp_path / "other" / "test.unknown").exists()

def test_sort_files_dry_run(tmp_path, capsys):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"img")
    rules = {"by_type": True, "by_date": False, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=True, safe=True)
    out = capsys.readouterr().out
    assert "[DRY RUN] Would move: test.jpg" in out
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
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=False, safe=True)
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
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=False, safe=False)
    # Should overwrite file
    assert (tmp_path / "images" / "test.jpg").read_bytes() == b"img"

def test_sort_files_custom_rule(tmp_path):
    receipt = tmp_path / "2024-receipt.pdf"
    receipt.write_bytes(b"receipt")
    rules = {"by_type": True, "by_date": False, "by_size": False, "custom": {"*-receipt.pdf": "Receipts"}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=False, safe=True)
    assert (tmp_path / "Receipts" / "2024-receipt.pdf").exists()

def test_sort_files_by_date(tmp_path):
    file = tmp_path / "old.txt"
    file.write_bytes(b"old")
    # Set mtime to Jan 2022
    old_time = datetime(2022, 1, 1).timestamp()
    os.utime(file, (old_time, old_time))
    rules = {"by_type": False, "by_date": True, "by_size": False, "custom": {}}
    type_folders = sort_files.load_config()["type_folders"]
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=False, safe=True)
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
    moved, skipped = sort_files.sort_files(tmp_path, rules, type_folders, dry_run=False, safe=True)
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
