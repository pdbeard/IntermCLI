# Output Handler

The Output Handler utility (`shared/output.py`) provides consistent output formatting with optional rich enhancements. It ensures a unified look and feel across all IntermCLI tools while gracefully degrading in environments without rich text support.

## Key Features

- Consistent formatting of messages, tables, and structured data
- Optional enhancement with [rich](https://github.com/Textualize/rich) when available
- Support for color, icons, and styling in supporting terminals
- Graceful fallback to plain text in non-supporting environments
- Progress indicators for long-running operations
- Hierarchical organization of output with headers and sections

## Usage

### Basic Usage

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Print different types of messages
output.info("Regular information message")
output.success("Operation completed successfully")
output.warning("Something might be wrong")
output.error("Something went wrong")
```

### Tool Banner and Configuration Display

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Display a tool banner with configuration details
output.banner("scan-ports", "1.0.0", {
    "Target": "example.com",
    "Ports": "1-1000",
    "Timeout": "2s"
})
```

This produces:
```
🔧 scan-ports v1.0.0
Target: example.com
Ports: 1-1000
Timeout: 2s
```

### Sections and Headers

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Display section headers
output.header("Scan Results")
# ... content ...

output.subheader("Open Ports")
# ... content ...

output.section("Details")
# ... content ...
```

This produces:
```
== Scan Results ==

-- Open Ports --

== Details ==
```

### Task Progress

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Indicate task start and completion
output.task_start("Scanning ports")
# ... do work ...
output.task_complete("Scanning ports", "Found 3 open ports")
```

This produces:
```
🔄 Starting Scanning ports...
✅ Completed Scanning ports: Found 3 open ports
```

### Key-Value Data

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Display key-value pairs
output.item("Host", "example.com")
output.item("Total ports", "1000")
output.item("Open ports", "3")
```

This produces:
```
Host: example.com
Total ports: 1000
Open ports: 3
```

### Tables

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Create and display a table
headers = ["Port", "State", "Service"]
rows = [
    ["22", "open", "SSH"],
    ["80", "open", "HTTP"],
    ["443", "open", "HTTPS"]
]
output.print_table(headers, rows)
```

This produces a nicely formatted table in supporting terminals.

### Progress Bars

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Create and use a progress bar
with output.create_progress_bar(total=100, description="Scanning") as progress:
    for i in range(100):
        # Do some work
        progress.update(1)
```

This shows a progress bar in supporting terminals and simpler progress output in non-supporting terminals.

### JSON and Markdown

```python
from shared.output import Output

# Initialize with tool name
output = Output("scan-ports")

# Display JSON data
data = {"host": "example.com", "ports": [22, 80, 443]}
output.print_json(data, "Scan Results")

# Display markdown content
markdown = """
# Scan Results

The scan of `example.com` found the following open ports:

- 22 (SSH)
- 80 (HTTP)
- 443 (HTTPS)
"""
output.print_markdown(markdown)
```

## Methods

| Method | Description |
|--------|-------------|
| `__init__(tool_name, use_rich=True, verbose=False)` | Initialize output handler |
| `info(message)` | Print information message |
| `success(message)` | Print success message |
| `warning(message)` | Print warning message |
| `error(message)` | Print error message |
| `debug(message)` | Print debug message (only if verbose enabled) |
| `banner(tool_name, version, details=None)` | Print tool banner |
| `header(message)` | Print section header |
| `subheader(message)` | Print subsection header |
| `section(name)` | Print section header (alternative style) |
| `task_start(task_name, details="")` | Print task start message |
| `task_complete(task_name, details="")` | Print task completion message |
| `item(key, value)` | Print key-value pair |
| `print_table(headers, rows)` | Print table |
| `create_progress_bar(total, description="Processing")` | Create progress bar |
| `print_json(data, title=None)` | Print JSON data |
| `print_markdown(markdown_text)` | Print markdown text |
| `separator(char="=", length=60)` | Print separator line |
| `blank()` | Print blank line |

## Best Practices

For detailed guidance on output styling and patterns, refer to the [Output Style Guide](../output-style-guide.md). Some key best practices include:

1. **Use appropriate message types** - info for general information, success for completion, warning for potential issues, error for problems
2. **Structure output hierarchically** - use headers, subheaders, and sections to organize output
3. **Show progress for long operations** - use progress bars or task start/complete messages
4. **Be consistent with formatting** - follow the style guide for all output
5. **Support both rich and plain environments** - let the Output class handle the differences

## See Also

- [Output Style Guide](../output-style-guide.md) - Comprehensive guide to output styling
- [Enhancement Loader](enhancement-loader.md) - For checking rich dependency
