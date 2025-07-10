import subprocess

def test_sort_files_help():
    result = subprocess.run(
        ["python3", "tools/sort-files/sort-files.py", "--help"],
        capture_output=True,
        text=True,
    )
    assert "usage" in result.stdout.lower()
    assert result.returncode == 0