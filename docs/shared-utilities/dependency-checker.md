# Dependency Checker

The Dependency Checker utility (`shared/dependency_checker.py`) handles detection and reporting of optional dependencies, enabling robust dependency management in IntermCLI tools.

## Purpose

IntermCLI tools are designed to work with minimal dependencies (Python standard library), but can provide enhanced functionality when optional dependencies are available. The Dependency Checker makes it easy to:

1. Check if optional dependencies are installed
2. Report missing dependencies to the user
3. Provide users with information about available enhancements
4. Fallback gracefully when dependencies are not available

## Usage

### Basic Usage

```python
from shared.dependency_checker import DependencyChecker

# Initialize with tool name
checker = DependencyChecker("scan-ports")

# Check for dependencies
has_requests = checker.check_dependency("requests")
has_rich = checker.check_dependency("rich")

# Use conditional logic based on available dependencies
if has_requests:
    import requests
    response = requests.get("https://example.com")
else:
    import urllib.request
    response = urllib.request.urlopen("https://example.com")
```

### Reporting Dependencies

```python
from shared.dependency_checker import DependencyChecker

# Initialize with tool name
checker = DependencyChecker("scan-ports")

# Check for dependencies
checker.check_dependency("requests")
checker.check_dependency("rich")
checker.check_dependency("cryptography")

# Print status (example)
for dep in ["requests", "rich", "cryptography"]:
    status = "Available" if checker.dependencies.get(dep) else "Missing"
    print(f"{dep}: {status}")
```

### Printing Status

```python
from shared.dependency_checker import DependencyChecker

# Initialize with tool name
checker = DependencyChecker("scan-ports")

# Check for dependencies
checker.check_dependency("requests")
checker.check_dependency("rich")
checker.check_dependency("cryptography")

# Print status
for dep in ["requests", "rich", "cryptography"]:
    status = "Available" if checker.dependencies.get(dep) else "Missing"
    print(f"{dep}: {status}")
```

### Checking for Missing Dependencies

```python
from shared.dependency_checker import DependencyChecker

# Initialize with tool name
checker = DependencyChecker("scan-ports")

# Check for dependencies
checker.check_dependency("requests")
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
