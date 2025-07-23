# Tool Metadata

The Tool Metadata utility (`shared/tool_metadata.py`) provides consistent version and documentation handling for IntermCLI tools. It extracts and formats tool information from docstrings and version data.

## Purpose

The Tool Metadata utility ensures that:

1. Tool description and examples are consistently formatted
2. Version information is displayed uniformly
3. Help text and banners follow a standard format
4. Documentation is extracted from tool docstrings

## Usage

### Basic Usage

```python
from shared.tool_metadata import ToolMetadata

# Create metadata object
metadata = ToolMetadata(
    tool_name="scan-ports",
    version="1.0.0",
    description="Scan ports on a remote host",
    examples=["scan-ports example.com", "scan-ports --range 1-1000 example.com"]
)

# Get formatted tool name with version
print(metadata.get_full_name())  # "scan-ports v1.0.0"

# Get tool banner
print(metadata.get_banner())  # "🔧 scan-ports v1.0.0 - Scan ports on a remote host"

# Get help text with examples
print(metadata.get_help_text())
```

### Creating Metadata from Module Docstring

```python
from shared.tool_metadata import ToolMetadata

# Create metadata from docstring
docstring = """
scan-ports: Scan ports on a remote host.

Find open ports on a target system with optional service detection.

Example usage:
    scan-ports example.com
    scan-ports --range 1-1000 example.com
    scan-ports --service-detection example.com
"""

metadata = ToolMetadata.from_module_docstring(
    tool_name="scan-ports",
    version="1.0.0",
    docstring=docstring
)
```

### Using Current Module's Metadata

```python
import sys
from shared.tool_metadata import ToolMetadata

# Initialize with tool info
TOOL_NAME = "scan-ports"
__version__ = "1.0.0"

# Get metadata from current module
metadata = ToolMetadata.for_current_tool(
    TOOL_NAME,
    __version__,
    sys.modules[__name__]
)

# Use in argument parser
from shared.arg_parser import ArgumentParser

parser = ArgumentParser(
    tool_name=TOOL_NAME,
    description=metadata.description,
    epilog=metadata.get_help_text(),
    version=__version__
)
```

## Methods

| Method | Description |
|--------|-------------|
| `__init__(tool_name, version, description, examples=None)` | Initialize tool metadata |
| `get_full_name()` | Get the full name with version |
| `get_banner()` | Get a banner for the tool |
| `get_help_text()` | Get formatted help text with description and examples |
| `from_module_docstring(tool_name, version, docstring)` | Create tool metadata from a module docstring |
| `for_current_tool(tool_name, version, module)` | Create tool metadata for the current tool |

## Docstring Format

The Tool Metadata utility expects docstrings in this format:

```python
"""
tool-name: Brief one-line description.

Optional multi-line detailed description.

Example usage:
    tool-name arg1
    tool-name --option value
    tool-name --flag
"""
```

- The first line is used as the tool description
- Lines after "Example usage:" are extracted as examples
- The docstring is parsed to extract this information automatically

## Integration with Other Utilities

Tool Metadata works well with other shared utilities:

```python
import sys
from shared.tool_metadata import ToolMetadata
from shared.arg_parser import ArgumentParser
from shared.output import Output

TOOL_NAME = "scan-ports"
__version__ = "1.0.0"

def main():
    # Get metadata from current module
    metadata = ToolMetadata.for_current_tool(
        TOOL_NAME,
        __version__,
        sys.modules[__name__]
    )

    # Use in argument parser
    parser = ArgumentParser(
        tool_name=TOOL_NAME,
        description=metadata.description,
        epilog=metadata.get_help_text(),
        version=__version__
    )

    # Parse arguments
    args = parser.parser.parse_args()

    # Initialize output
    output = Output(TOOL_NAME)

    # Display banner with metadata
    output.banner(TOOL_NAME, __version__, {
        "Description": metadata.description
    })
```

## Best Practices

1. **Write clear, concise docstrings** for your tools
2. **Include practical examples** in your docstrings
3. **Use the metadata consistently** in banners and help text
4. **Extract metadata from docstrings** rather than duplicating information

## See Also

- [Argument Parser](argument-parser.md) - For using metadata in argument parsing
- [Output Handler](output-handler.md) - For displaying tool banners with metadata
