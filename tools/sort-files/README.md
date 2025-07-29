## sort-files

Organize and declutter directories by automatically sorting files into subfolders based on file type, date, size, or user-defined custom rules.

### Usage

```bash
sort-files ~/Downloads                # Sort files by type in Downloads
sort-files --by date ~/Documents      # Sort files by date
sort-files --copy ~/Desktop           # Copy files instead of moving them
sort-files --recursive ~/Projects     # Process subdirectories recursively
sort-files --dry-run --show-skipped ~/Desktop   # Preview actions, show skipped files
sort-files --config ~/.config/intermcli/sort-files.toml ~/Downloads  # Use custom config
```

### Features
- Sort by type, date, or size
- Copy or move files (--copy flag)
- Recursively process subdirectories (--recursive or -r)
- Custom rules via TOML config
- Dry run mode for preview
- Safe by default (never overwrites files)
- Cross-platform (Linux, macOS)
- TOML-based configuration

### Configuration
- Uses TOML config at `tools/sort-files/config/defaults.toml` (or custom path)
- Configuration follows the IntermCLI hierarchy (tool defaults, user global, user tool-specific, project local)
- You can add, remove, or customize type folders and rules.
- All settings are defined in the configuration file, no hardcoded values.
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
