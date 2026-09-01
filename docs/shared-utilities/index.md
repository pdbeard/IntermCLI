# Shared Utilities

IntermCLI provides a set of shared utilities that can be used across all tools in the suite. These utilities help maintain consistency, reduce code duplication, and make the codebase more maintainable.

## Available Utilities

| Utility | Description | File |
|---------|-------------|------|
| [Config Loader](config-loader.md) | Handles TOML configuration loading with proper precedence | `shared/config_loader.py` |
| [Dependency Checker](dependency_checker.md) | Handles detection of optional dependencies | `shared/dependency_checker.py` |
| [Output Handler](output-handler.md) | Provides consistent output formatting | `shared/output.py` |
| [Error Handler](error-handler.md) | Provides standardized error handling | `shared/error_handler.py` |
| [Argument Parser](argument-parser.md) | Provides consistent argument parsing | `shared/arg_parser.py` |
| [Path Utilities](path-utils.md) | Ensures shared modules can be imported properly | `shared/path_utils.py` |
| [Tool Metadata](tool-metadata.md) | Provides consistent version and documentation handling | `shared/tool_metadata.py` |

## Using Shared Utilities

For detailed documentation on how to use each utility, click on the utility name above. For a complete example of using all utilities together, see [Integration Example](integration-example.md).

## See Also

- [Output Style Guide](../output-style-guide.md) - Guidelines for consistent output formatting
- [Developer Guide](../DEVELOPER-GUIDE.md) - Architecture, design principles, and contribution workflow
