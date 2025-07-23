# Path Utilities

The Path Utilities module (`shared/path_utils.py`) ensures shared modules can be imported properly by tools, regardless of how they are invoked. It handles Python path management to make shared utilities accessible.

## Purpose

The Path Utilities module solves a common problem in Python projects with a shared module structure: ensuring that tools can import shared modules regardless of:

1. Where the tool is located in the filesystem
2. How the tool is invoked (directly, via symlink, installed via pip, etc.)
3. The current working directory

## Key Functions

### `add_shared_path()`

Adds the shared module directory to the Python path, allowing tools to import shared modules.

```python
from shared.path_utils import add_shared_path

# Add the shared path to sys.path
add_shared_path()

# Now you can import shared modules
from shared import config_loader, output
```

### `ensure_shared_imports()`

Checks if shared modules can be imported, and if not, adds the necessary path.

```python
from shared.path_utils import ensure_shared_imports

# Check if shared imports are available
if ensure_shared_imports():
    # Shared modules are available
    from shared import config_loader, output
else:
    print("Shared modules could not be imported")
```

### `require_shared_utilities()`

Ensures shared utilities are available or exits with a helpful message.

```python
# This is typically used at the beginning of a tool script
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from shared.path_utils import require_shared_utilities
    require_shared_utilities()
except ImportError:
    # If even path_utils can't be imported, provide a fallback error
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

# Now safely import other shared modules
from shared.config_loader import ConfigLoader
from shared.output import Output
```

## Usage in Tools

The typical usage pattern in an IntermCLI tool is:

```python
#!/usr/bin/env python3
"""
my-tool: Brief description of what the tool does.
"""

import sys
from pathlib import Path

# Ensure shared utilities are available
parent_path = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, parent_path)
try:
    from shared.path_utils import require_shared_utilities
    require_shared_utilities()
except ImportError:
    # If even path_utils can't be imported, provide a fallback error
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

# Now safely import other shared modules
from shared.config_loader import ConfigLoader
from shared.output import Output
from shared.enhancement_loader import EnhancementLoader
from shared.arg_parser import ArgumentParser

# Rest of the tool...
```

## Methods

| Function | Description |
|----------|-------------|
| `add_shared_path()` | Add the shared module directory to the Python path |
| `ensure_shared_imports()` | Ensure shared modules can be imported, adding path if necessary |
| `require_shared_utilities()` | Ensure shared utilities are available or exit with a helpful message |

## Best Practices

1. **Always use `require_shared_utilities()`** at the beginning of your tool
2. **Handle import errors gracefully** with helpful error messages
3. **Use absolute paths** when determining the location of shared modules
4. **Don't assume the current working directory** is the tool's directory

## See Also

- [CONTRIBUTING Guide](../CONTRIBUTING.md) - Guide for project contributors
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Guidelines for contributing to IntermCLI
