# Output Style Guide

This document defines the standard patterns, formatting conventions, and best practices for output formatting across all IntermCLI tools. Following these guidelines ensures a consistent, user-friendly, and accessible experience across the entire suite.

## Core Principles

1. **Consistency** - All tools should present information in a consistent manner
2. **Progressive Enhancement** - Output should degrade gracefully without rich formatting
3. **User-Focused** - Output should be clear, scannable, and helpful
4. **Task-Oriented** - Structure output around the user's workflow and tasks
5. **Accessibility** - Support both rich and plain text environments
6. **Contextual Information** - Provide appropriate context without overwhelming users

## Standard Output Patterns

### Tool Identification

Every tool should identify itself at startup using the `banner()` method:

```python
output.banner(TOOL_NAME, __version__, {
    "Description": "Brief description of the tool",
    "Mode": mode
})
```

This produces output like:
```
🔧 tool-name v1.0.0
Description: Brief description of the tool
Mode: standard
```

### Common Patterns by Context

#### Starting a Task

When starting a task, provide a clear indication of what's about to happen:

```python
output.task_start(task_name)
# or for more specific contexts
output.task_start("Processing files", f"{total_items} files in {target_dir}")
```

This produces output like:
```
🔄 Starting Processing files... 42 files in /path/to/dir
```

#### Completing a Task

When completing a task, provide a clear success message with relevant statistics:

```python
output.task_complete(task_name)
# or for more specific contexts
output.task_complete("Processing files", f"{files_processed} of {total_files} processed")
```

This produces output like:
```
✅ Completed Processing files: 42 of 42 processed
```

#### Warnings

When something requires user attention but doesn't prevent operation:

```python
output.warning(f"Some items ({count}) were skipped. Use --show-skipped to see details.")
```

#### Errors

When something prevents successful operation:

```python
output.error(f"Failed to {action}: {reason}")
```

#### Headers and Sections

For major sections, use a consistent header format:

```python
output.header("Main Section")       # Main section header
output.subheader("Subsection")      # Subsection header
output.section("Results Section")   # Alternative section header
```

This produces output like:
```
== Main Section ==

-- Subsection --

== Results Section ==
```

### Tabular Data

Use tables for structured data:

```python
# Using the create_table method
table = output.create_table(title="Summary", headers=["Category", "Count"])
for category, count in data.items():
    table.add_row(category, str(count))
output.print_table(table)

# Using the print_table method directly with headers and rows
headers = ["Category", "Count"]
rows = [["Documents", "42"], ["Images", "17"], ["Other", "5"]]
output.print_table(headers, rows)
```

This produces a nicely formatted table:
```
┌─────────────┬───────┐
│ Category    │ Count │
├─────────────┼───────┤
│ Documents   │ 42    │
│ Images      │ 17    │
│ Other       │ 5     │
└─────────────┴───────┘
```

Or in plain text mode:
```
Category    | Count
------------+------
Documents   | 42
Images      | 17
Other       | 5
```

### Key-Value Data

For displaying configuration or properties:

```python
output.item("Source", source_path)
output.item("Destination", dest_path)
output.item("Total Files", str(total_files))
```

This produces:
```
Source: /path/to/source
Destination: /path/to/destination
Total Files: 42
```

### Progress Indication

For long-running operations, provide progress updates:

```python
with output.create_progress_bar(total=total_items, description="Processing files") as progress:
    for item in items:
        # Process item
        progress.update(1)
```

This produces a rich progress bar when available:
```
Processing files [████████████████████] 42/42
```

Or a simpler text-based progress indicator in plain text mode.

## Visual Styling

### Color Usage

Colors should be used consistently to convey meaning:

- **Green** - Success, completion, positive outcomes
- **Yellow** - Warnings, caution, items requiring attention
- **Red** - Errors, failures, critical issues
- **Cyan** - Information, general status, neutral content
- **Magenta/Bold Cyan** - Highlights, important data points, attention-grabbing elements
- **Dim** - Less important or contextual information

### Icons

Use consistent icons across all tools to reinforce meaning:

- **Tool**: 🔧 - Tool identification
- **Success**: ✅ - Successful operations
- **Warning**: ⚠️ - Warnings, caution
- **Error**: ❌ - Errors, failures
- **Processing/Loading**: � - In-progress operations
- **Search/Find**: 🔍 - Search operations
- **Lists/Summary**: 📋 - Summaries, results
- **File Operations**: 📁 - File or directory operations
- **Network**: 🌐 - Network operations
- **Security**: 🔒 - Security operations
- **Settings**: ⚙️ - Configuration
- **Directory/Folder**: 📁 - Directory operations
- **Organizing/Sorting**: 🗃️ - Sorting or organizing operations
- **Time/Clock**: ⏱️ - Timing operations
- **Information**: ℹ️ - Informational messages

### Indentation and Hierarchy

- Use consistent indentation for hierarchical data
- Indent detailed information under main headings
- Use clear visual separation between sections

## Implementation Examples

### Tool Banner and Configuration Display

```python
# Using banner method
output.banner(TOOL_NAME, __version__, {
    "Target": str(target_dir),
    "Rule": rule,
    "Dry run": "ON" if config["dry_run"] else "OFF"
})

# Alternative with individual calls
output.info(f"🔧 {TOOL_NAME} v{__version__}")
output.info(f"Target: {target_dir}")
output.info(f"Rule: {rule}")
output.info(f"Dry run: {'ON' if config['dry_run'] else 'OFF'}")
```

### Task Workflow Example

```python
# Start a workflow with a main header
output.header("Processing Files")

# Start a specific task
output.task_start("Analyzing files", f"{total_files} files in {target_dir}")

# ... operations ...

# Indicate task completion
output.task_complete("Analyzing files", f"Found {issues} issues")

# Create a subsection for details
output.subheader("Details")

# Show results in a table
headers = ["File", "Issue"]
rows = [(file, issue) for file, issue in issues.items()]
output.print_table(headers, rows)
```

### Complete Tool Flow Example

```python
def main():
    # Setup output
    output = Output(TOOL_NAME, verbose=args.verbose)

    # Display banner
    output.banner(TOOL_NAME, __version__, {
        "Target": str(target_dir),
        "Mode": mode,
        "Dry run": "ON" if dry_run else "OFF"
    })

    # Process input
    output.task_start("Validating input")
    # ... validation logic ...
    output.task_complete("Validating input", "All inputs valid")

    # Main operation
    output.header("Processing Data")
    output.info(f"Found {total_items} items to process")

    with output.create_progress_bar(total=total_items, description="Processing") as progress:
        for item in items:
            # ... process item ...
            progress.update(1)

    # Results
    output.header("Results")

    if processed:
        output.success(f"Successfully processed {len(processed)} items")

        # Summary table
        output.subheader("Summary")
        headers = ["Category", "Count"]
        rows = [(cat, str(count)) for cat, count in counts.items()]
        output.print_table(headers, rows)

    if errors:
        output.error(f"Failed to process {len(errors)} items")
        output.subheader("Errors")
        for item, error in errors.items():
            output.info(f"  {item}: {error}")
```

## Best Practices

### General Guidelines

1. **Be Consistent** - Follow the same patterns across all tools
2. **Be Concise** - Keep output clear and to the point
3. **Be Informative** - Provide context and explain what's happening
4. **Be Helpful** - Provide next steps or suggestions when appropriate
5. **Be Accessible** - Ensure output works well in all environments

### Verbosity Levels

- **Default** - Show essential information only
- **Verbose** - Show detailed progress and additional context
- **Quiet** - Show only errors and final results

### Error Handling

- Be specific about what went wrong
- Suggest possible solutions when errors occur
- Use appropriate exit codes
- Group related errors when possible

### Output Volume

- Group related information
- Use hierarchical structure to organize complex output
- Consider pagination for very large outputs

### Terminal Width

- Respect terminal width when possible
- Wrap or truncate long lines appropriately
- Use horizontal separators consistently

### Machine Readability

- Support JSON output option for scripting/automation
- Consistent exit codes
- Structured error messages

## Integration with Shared Output Utility

The `shared.output.Output` class provides methods that implement these patterns.
Always use these methods rather than direct prints or custom formatting:

| Method | Purpose |
|--------|---------|
| `banner()` | Display tool identification banner |
| `header()` | Display a main section header |
| `subheader()` | Display a subsection header |
| `section()` | Alternative section header |
| `task_start()` | Indicate the start of a task |
| `task_complete()` | Indicate the completion of a task |
| `info()` | Display general information |
| `warning()` | Display a warning message |
| `error()` | Display an error message |
| `success()` | Display a success message |
| `debug()` | Display debug information (verbose only) |
| `item()` | Display a key-value pair |
| `print_table()` | Display tabular data |
| `create_progress_bar()` | Create a progress indicator |
| `print_json()` | Display JSON data |
| `print_markdown()` | Display formatted markdown text |

## Accessibility Considerations

- All colored output should have text indicators as well (icons, formatting)
- Follow terminal color contrast guidelines
- Support NO_COLOR environment variable
- Provide non-graphical alternatives for progress indicators

## See Also

- [CONTRIBUTING.md](/docs/CONTRIBUTING.md) - For contributors creating new tools
- [shared-utilities.md](/docs/shared-utilities.md) - Documentation for shared utilities
