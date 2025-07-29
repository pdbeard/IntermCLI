# Error Handler

The shared error handler provides standardized error handling across all IntermCLI tools. It ensures consistent error messaging, logging, and behavior for common error types.

## Overview

The `error_handler` module provides a unified approach to handling errors in a consistent way across all tools in the IntermCLI suite. It integrates with the Output utility to ensure error messages are displayed consistently and can be customized for different output formats.

Key features:
- Standardized error codes for programmatic handling
- User-friendly error messages
- Integration with the Output utility
- Specialized handlers for common operations (files, network, config, etc.)
- Optional automatic exit on critical errors

## Basic Usage

```python
from shared.error_handler import ErrorHandler
from shared.output import Output

# Initialize
output = Output(TOOL_NAME)
error_handler = ErrorHandler(output)

# Handle file errors
try:
    with open(some_file, 'r') as f:
        content = f.read()
except Exception as e:
    msg, code = error_handler.handle_file_operation(some_file, e, operation="read")
    # Handle accordingly (skip, exit, etc.)
```

## Error Categories

The error handler provides specialized handling for different categories of errors:

### File Operations

For file-related errors like permissions, not found, etc.:

```python
try:
    shutil.move(src, dest)
except Exception as e:
    msg, code = error_handler.handle_file_operation(file_path, e, operation="move")
```

### Network Operations

For network-related errors like connection failures, timeouts, etc.:

```python
try:
    response = requests.get(url)
except Exception as e:
    msg, code = error_handler.handle_network_operation(url, e, operation="download")
```

### Configuration Errors

For errors related to configuration files:

```python
try:
    config = config_loader.load_config()
except Exception as e:
    msg, code = error_handler.handle_config_error(config_path, e)
```

### Dependency Errors

For errors related to missing or incompatible dependencies:

```python
try:
    import some_library
except Exception as e:
    msg, code = error_handler.handle_dependency_error("some_library", e)
```

### Resource Errors

For errors related to system resources:

```python
try:
    # Some operation that might use a lot of memory
    process_large_dataset()
except Exception as e:
    msg, code = error_handler.handle_resource_error("memory", "dataset processing", e)
```

## Error Codes

Error codes follow a consistent format: `category:specific_error`. For example:
- `file:not_found`
- `network:connection_error`
- `config:invalid_toml`
- `dependency:not_installed`
- `resource:memory`

These codes can be used for programmatic handling of errors:

```python
msg, code = error_handler.handle_file_operation(file_path, e)
if code == "file:not_found":
    # Handle missing file case
elif code == "file:permission_denied":
    # Handle permission issues
```

## Convenience Functions

For one-off error handling, convenience functions are provided:

```python
from shared.error_handler import handle_file_error

try:
    with open(file_path, 'r') as f:
        content = f.read()
except Exception as e:
    msg, code = handle_file_error(output, file_path, e, operation="read")
```

## Function Wrapping

You can wrap functions with error handling:

```python
def risky_operation(file_path):
    # Some operation that might fail

# Create a wrapped version
safe_operation = error_handler.with_error_handling(
    risky_operation,
    lambda e: error_handler.handle_file_operation(file_path, e),
    exit_on_error=False
)

# Call the wrapped function
result = safe_operation(file_path)
```

## Integration with Other Shared Utilities

The error handler integrates seamlessly with other shared utilities:

- **Output**: For consistent error message formatting
- **Config Loader**: For handling configuration errors
- **Enhancement Loader**: For handling dependency errors
