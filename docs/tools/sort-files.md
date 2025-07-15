# 🗃️ sort-files

**sort-files** is a terminal utility for organizing files in a directory by type, date, size, or custom rules.
It is part of the IntermCLI suite and follows the action-target naming convention.

---

## 🚀 Purpose

Help users quickly organize cluttered directories (like Downloads, Desktop, or project folders) by sorting files into subfolders based on user-defined or common criteria.

---

## ✨ Features

- **Sort by File Type**
  Move files into folders by extension (e.g., `images/`, `documents/`, `archives/`, etc.)

- **Sort by Date**
  Organize files into folders by creation or modification date (e.g., `2025-07/`, `2025-07-02/`).

- **Sort by Size**
  Move large files into a separate folder, or group by size ranges.

- **Custom Rules**
  User-defined patterns via TOML config (e.g., move `*-receipt.pdf` to `Receipts/`).

- **Dry Run Mode**
  Preview what changes would be made without actually moving files.

- **Safe by Default**
  Never overwrite files without confirmation; handle name collisions gracefully.

- **Configurable via TOML**
  User and project-level config files for custom rules and folder mappings.

- **Cross-Platform**
  Works on Linux, macOS, and Windows.

---

## 📝 Example Usage

```bash
sort-files ~/Downloads
sort-files --by type ~/Desktop
sort-files --by date --dry-run ~/Documents
sort-files --config ~/.config/intermcli/sort-files.toml ~/Downloads
```

---

## ⚙️ Configuration

Configuration is TOML-based and can be set globally, per-project, or per-invocation.

**Example: `tools/sort-files/config/defaults.toml`**
```toml
skip_hidden = true
skip_dirs = []

[rules]
by_type = true
by_date = false
by_size = false

[rules.custom]
"*-receipt.pdf" = "Receipts"
"*-bill.pdf" = "Bills"

[type_folders]
images = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"]
documents = [".pdf", ".docx", ".doc", ".txt", ".md", ".odt", ".rtf", ".xls", ".xlsx", ".csv"]
archives = [".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"]
audio = [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"]
video = [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm"]
code = [".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rb", ".php", ".sh", ".rs"]
```

---

## 🧪 Behavior Notes

- **Custom rules** (e.g., `*-receipt.pdf`) take precedence over type/date/size sorting.
- Files with unknown or no extension are placed in the `other/` folder.
- Hidden files and directories are skipped by default.
- No files are overwritten unless `--unsafe` is specified.

---

## 🔮 Future Ideas

- Interactive mode (TUI) for manual review and sorting
- Undo/restore log for moved files
- Bulk rename and symlink/copy support
- Integration with other IntermCLI tools (e.g., find-duplicates, deduplicate)
- Scheduling/automation support

---

## 🐍 Requirements


- No dependencies required for core features
- Optional: `rich` for colorized output, `tomli` for config on Python <3.11

---

## 📚 See Also

- [find-duplicates](./find-duplicates.md)
- [bulk-rename](./bulk-rename.md)
- [organize-downloads](./organize-downloads.md)

---

Help us shape this tool!
Open an issue or PR with your feature ideas or use cases.
