# sort-files

Organize and declutter directories by automatically sorting files into subfolders based on type, date, size, or custom rules.

## Usage

```bash
# Sort files by type (default)
sort-files ~/Downloads

# Sort files by date
sort-files --by date ~/Documents

# Copy files instead of moving them
sort-files --copy ~/Desktop

# Process subdirectories recursively
sort-files --recursive ~/Projects

# Preview actions without making changes
sort-files --dry-run ~/Desktop

# Use custom configuration
sort-files --config ~/.config/intermcli/sort-files.toml ~/Downloads
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--by` | `type` | Sorting method: type, date, size, or custom |
| `--copy` | `false` | Copy files instead of moving them |
| `--recursive`, `-r` | `false` | Process subdirectories recursively |
| `--dry-run` | `false` | Preview actions without making changes |
| `--config` | Tool default | Path to custom configuration file |
| `--show-skipped` | `false` | Display files that were skipped |
| `--verbose` | `false` | Show detailed information during processing |

## Advanced Usage

For custom sorting rules and file type mapping, see the [comprehensive documentation](../docs/tools/sort-files.md).

## Features

- Sort by file type, date, or size
- Copy or move files with safe overwrite protection
- Recursively process subdirectories
- Custom rules via TOML configuration
- Dry run mode for previewing changes
- Safe by default (never overwrites existing files)
- Cross-platform compatibility (Linux, macOS)
- TOML-based configuration without hardcoded values
- If TOML support is missing, the tool will display an error message.

**Example TOML snippet:**
```toml
[rules]
by_type = true
by_date = false
by_size = false

[type_folders]
images = [".jpg", ".jpeg", ".png", ".gif"]
documents = [".pdf", ".docx", ".txt"]
archives = [".zip", ".tar", ".gz"]
```

### Customizing
- Edit the TOML config to add new folders, rules, or patterns.
- Use `sort-files --config <path>` to specify a custom config file.

### Troubleshooting
- If you see "TOML support not available", install `tomli` for Python < 3.11: `pip install tomli`
- If the config file is missing, the tool will fall back to built-in defaults.

### Options

```
--by {type,date,size}    How to organize files (default: type)
--config CONFIG          Path to configuration file
--dry-run                Show what would be done without moving files
--copy                   Copy files instead of moving them
--recursive, -r          Process subdirectories recursively
--unsafe                 Allow overwriting files in destination
--show-skipped           Show skipped files
--check-deps             Check optional dependency status
```
