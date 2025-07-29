# Enhancement Loader

The Enhancement Loader utility (`shared/enhancement_loader.py`) handles detection of optional dependencies and provides consistent information about available enhancements, enabling "progressive enhancement" in IntermCLI tools.

## Purpose

IntermCLI tools are designed to work with minimal dependencies (Python standard library), but can provide enhanced functionality when optional dependencies are available. The Enhancement Loader makes it easy to:

1. Check if optional dependencies are installed
2. Register features that depend on these dependencies
3. Provide users with information about available enhancements
4. Fallback gracefully when dependencies are not available

## Usage

### Basic Usage

```python
from shared.enhancement_loader import EnhancementLoader

# Initialize with tool name
enhancements = EnhancementLoader("scan-ports")

# Check for dependencies
has_requests = enhancements.check_dependency("requests")
has_rich = enhancements.check_dependency("rich")

# Use conditional logic based on available dependencies
if has_requests:
    # Use requests library for HTTP requests
    import requests
    response = requests.get("https://example.com")
else:
    # Fallback to standard library
    import urllib.request
    response = urllib.request.urlopen("https://example.com")
```

### Registering Features

```python
from shared.enhancement_loader import EnhancementLoader

# Initialize with tool name
enhancements = EnhancementLoader("scan-ports")

# Check for dependencies
enhancements.check_dependency("requests")
enhancements.check_dependency("rich")
enhancements.check_dependency("cryptography")

# Register features that depend on these dependencies
enhancements.register_feature("enhanced_http", ["requests"])
enhancements.register_feature("rich_output", ["rich"])
enhancements.register_feature("secure_connections", ["cryptography", "requests"])

# Check if a feature is available
if enhancements.is_feature_available("rich_output"):
    # Use rich for enhanced output
    from rich.console import Console
    console = Console()
    console.print("Enhanced output enabled")
```

### Printing Status

```python
from shared.enhancement_loader import EnhancementLoader

# Initialize with tool name
enhancements = EnhancementLoader("scan-ports")

# Check for dependencies
enhancements.check_dependency("requests", "HTTP Client")
enhancements.check_dependency("rich", "Rich Output")
enhancements.check_dependency("cryptography", "Secure Connections")

# Print status
enhancements.print_status()
```

This will produce output like:

```
Optional Dependencies:
✅ HTTP Client (requests): Available
❌ Rich Output (rich): Not available
✅ Secure Connections (cryptography): Available
```

### Checking for Missing Dependencies

```python
from shared.enhancement_loader import EnhancementLoader

# Initialize with tool name
enhancements = EnhancementLoader("scan-ports")

# Check for dependencies
enhancements.check_dependency("requests")
enhancements.check_dependency("rich")

# Get missing dependencies
missing_deps = enhancements.get_missing_dependencies()

# Suggest installation if needed
if missing_deps:
    print(f"For full functionality, install: {', '.join(missing_deps)}")
```

## Methods

| Method | Description |
|--------|-------------|
| `__init__(tool_name, logger=None)` | Initialize enhancement loader for a specific tool |
| `check_dependency(module_name, alias=None)` | Check if a dependency is available |
| `register_feature(feature_name, dependencies)` | Register a feature that depends on specific dependencies |
| `is_feature_available(feature_name)` | Check if a feature is available (all dependencies satisfied) |
| `get_missing_dependencies()` | Get a list of missing dependencies |
| `print_status()` | Print a formatted status of all dependencies |

## Best Practices

1. **Always fallback to standard library** when optional dependencies aren't available
2. **Check dependencies early** in your tool's execution
3. **Register features** that depend on multiple dependencies
4. **Provide a `--check-deps` flag** in your tool to show dependency status
5. **Use meaningful aliases** for dependencies to make them user-friendly

## See Also

- [Output Handler](output-handler.md) - For consistent output formatting
- [Argument Parser](argument-parser.md) - For handling the `--check-deps` flag
