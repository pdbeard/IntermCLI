# Output Style Guide

This guide defines the standard formatting conventions for all IntermCLI tools. Following these guidelines ensures a consistent, user-friendly experience across the entire suite.

## Core Principles

1. **Consistency** - Unified formatting across all tools
2. **Progressive Enhancement** - Rich formatting when available, clear plain text otherwise
3. **User-Focused** - Clear, scannable, and helpful information
4. **Task-Oriented** - Output structured around user workflows
5. **Accessibility** - Support for both rich and plain text environments

## Standard Output Format

All tools use the shared output utility (`shared/output.py`) for consistent formatting:

```python
from shared.output import banner, header, info, success, warning, error

# Tool identification
banner("Find Projects", "1.0.0", {
    "Description": "Interactive project discovery tool"
})

# Section header
header("Search Results")

# Informational message
info("Scanning directories...")

# Success message
success("Found 12 projects")

# Warning message
warning("Some directories were skipped due to permissions")

# Error message
error("Unable to access network resources")
```

## Message Types

| Type | Use Case | Styling |
|------|----------|---------|
| Banner | Tool identification | Cyan with version |
| Header | Section headings | Bold, tool color |
| Info | Status updates, general information | Standard text |
| Success | Completion messages, positive outcomes | Green text with ✅ |
| Warning | Non-blocking issues, potential problems | Yellow text with ⚠️ |
| Error | Failures, blocking issues | Red text with ❌ |
| Debug | Troubleshooting information (verbose mode only) | Dim text |

## Structured Data

For presenting structured data:

```python
# Tables
headers = ["Name", "Type", "Modified"]
rows = [["project1", "Python", "Today"], ["project2", "Go", "Yesterday"]]
output.print_table(headers, rows)

# Key-value pairs
output.item("Total", "42 items")
output.item("Location", "/path/to/directory")
```

## Interactive Elements

For interactive elements, use the following patterns:

```python
# User prompt
response = output.prompt("Enter search path")

# Confirmation
if output.confirm("Delete 5 files?"):
    # proceed with deletion

# Selection from options
option = output.select("Sort by", ["name", "date", "size"])

# Progress indication
with output.create_progress_bar(total=len(files), description="Processing") as progress:
    for file in files:
        process_file(file)
        progress.update(1)
```

## Rich Formatting Support

When the `rich` package is available, enhanced formatting will be used automatically:

- Syntax highlighting for code blocks
- Tables for structured data
- Progress bars for long-running operations
- Hyperlinks for URLs and file paths

Plain text alternatives are always provided when rich formatting is unavailable.

## Implementation

The shared output module handles all formatting details, including:

- Automatic detection of terminal capabilities
- Color and styling based on terminal support
- Fallbacks for plain text environments
- Consistent spacing and alignment

For complete implementation details, see the [Shared Utilities Reference](./shared-utilities-reference.md#output-handler-outputpy).
