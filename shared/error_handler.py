#!/usr/bin/env python3
"""
Error handling utilities for IntermCLI tools.
Provides consistent error handling and messaging across the IntermCLI suite.

This module offers standardized error handling for common operations:
- File system operations
- Network operations
- Permission issues
- Configuration errors
- Resource errors

Each handler returns both a user-friendly message and a standardized error code
that can be used for programmatic handling of errors.
"""

import sys
from pathlib import Path
from typing import Callable, Tuple, Union

from .output import Output


class ErrorHandler:
    """
    Handles errors consistently across IntermCLI tools.

    This class provides standardized error handling for common operations,
    with integration to the shared Output utility for consistent messaging.

    Typical usage:
        error_handler = ErrorHandler(output)
        try:
            # Some operation that might fail
            do_something_risky()
        except Exception as e:
            msg, code = error_handler.handle_file_operation(path, e)
            # Handle the error (log, exit, skip, etc.)
    """

    def __init__(self, output: Output, exit_on_critical: bool = False):
        """
        Initialize the error handler.

        Args:
            output: Output utility for displaying messages
            exit_on_critical: If True, automatically exit on critical errors
        """
        self.output = output
        self.exit_on_critical = exit_on_critical

    def _handle_generic(
        self, context: str, exception: Exception, prefix: str = "error"
    ) -> Tuple[str, str]:
        """
        Generic error handler for any exception.

        Args:
            context: Description of what was being attempted
            exception: The exception that was raised
            prefix: Prefix for the error code

        Returns:
            Tuple of (error_message, error_code)
        """
        exception_name = type(exception).__name__
        msg = f"{context}: {exception}"
        code = f"{prefix}:{exception_name}"
        self.output.error(msg)
        return msg, code

    def handle_file_operation(
        self, path: Path, exception: Exception, operation: str = "access"
    ) -> Tuple[str, str]:
        """
        Handle errors when working with files.

        Args:
            path: The file that was being operated on
            exception: The exception that was raised
            operation: The operation being performed (access, create, delete, etc.)

        Returns:
            Tuple containing (error_message, error_code)
        """
        filename = path.name

        if isinstance(exception, PermissionError):
            msg = (
                f"Failed to {operation} {filename}: Permission denied. "
                f"Try running with elevated permissions."
            )
            code = "file:permission_denied"
        elif isinstance(exception, FileNotFoundError):
            msg = (
                f"Failed to {operation} {filename}: File not found. "
                f"It may have been moved or deleted."
            )
            code = "file:not_found"
        elif isinstance(exception, FileExistsError):
            msg = f"Failed to create {filename}: File already exists."
            code = "file:exists"
        elif isinstance(exception, IsADirectoryError):
            msg = f"Failed to {operation} {filename}: Is a directory, not a file."
            code = "file:is_directory"
        elif isinstance(exception, NotADirectoryError):
            msg = f"Failed to {operation} {filename}: Is a file, not a directory."
            code = "file:not_directory"
        elif isinstance(exception, OSError) and exception.errno == 28:
            msg = f"Failed to {operation} {filename}: No space left on device."
            code = "file:no_space"
        elif isinstance(exception, OSError) and exception.errno == 30:
            msg = f"Failed to {operation} {filename}: Read-only file system."
            code = "file:read_only_fs"
        else:
            return self._handle_generic(
                f"Failed to {operation} {filename}", exception, "file"
            )

        self.output.error(msg)
        return msg, code

    def handle_network_operation(
        self, resource: str, exception: Exception, operation: str = "access"
    ) -> Tuple[str, str]:
        """
        Handle errors for network operations.

        Args:
            resource: The resource being accessed (URL, hostname, etc.)
            exception: The exception that was raised
            operation: The operation being performed (connect, download, etc.)

        Returns:
            Tuple containing (error_message, error_code)
        """
        # Common network-related exceptions
        if isinstance(exception, ConnectionError):
            msg = (
                f"Failed to {operation} {resource}: Connection error. "
                f"Check your network connection."
            )
            code = "network:connection_error"
        elif isinstance(exception, TimeoutError):
            msg = f"Failed to {operation} {resource}: Connection timed out."
            code = "network:timeout"
        elif hasattr(exception, "getcode") and callable(exception.getcode):
            # Handle urllib.error.HTTPError-like objects
            try:
                status_code = exception.getcode()
                msg = f"Failed to {operation} {resource}: HTTP error {status_code}."
                code = f"network:http_{status_code}"
            except Exception:
                return self._handle_generic(
                    f"Failed to {operation} {resource}", exception, "network"
                )
        else:
            return self._handle_generic(
                f"Failed to {operation} {resource}", exception, "network"
            )

        self.output.error(msg)
        return msg, code

    def handle_config_error(
        self, config_path: Union[str, Path], exception: Exception
    ) -> Tuple[str, str]:
        """
        Handle errors related to configuration files.

        Args:
            config_path: Path to the configuration file
            exception: The exception that was raised

        Returns:
            Tuple containing (error_message, error_code)
        """
        filename = Path(config_path).name

        if isinstance(exception, FileNotFoundError):
            msg = f"Configuration file not found: {filename}"
            code = "config:not_found"
        elif isinstance(exception, PermissionError):
            msg = f"Permission denied when reading configuration file: {filename}"
            code = "config:permission_denied"
        elif "JSONDecodeError" in str(type(exception)):
            msg = f"Invalid JSON in configuration file: {filename}"
            code = "config:invalid_json"
        elif "TomlDecodeError" in str(type(exception)):
            msg = f"Invalid TOML in configuration file: {filename}"
            code = "config:invalid_toml"
        elif "YAMLError" in str(type(exception)):
            msg = f"Invalid YAML in configuration file: {filename}"
            code = "config:invalid_yaml"
        else:
            return self._handle_generic(
                f"Error in configuration file {filename}", exception, "config"
            )

        self.output.error(msg)
        return msg, code

    def handle_dependency_error(
        self, dependency: str, exception: Exception
    ) -> Tuple[str, str]:
        """
        Handle errors related to missing or incompatible dependencies.

        Args:
            dependency: Name of the dependency
            exception: The exception that was raised

        Returns:
            Tuple containing (error_message, error_code)
        """
        if isinstance(exception, ImportError):
            msg = (
                f"Required dependency '{dependency}' is not installed. "
                f"Install it with: pip install {dependency}"
            )
            code = "dependency:not_installed"
        elif isinstance(exception, AttributeError):
            msg = (
                f"Incompatible version of '{dependency}'. "
                f"Please update it with: pip install --upgrade {dependency}"
            )
            code = "dependency:incompatible"
        else:
            return self._handle_generic(
                f"Error with dependency '{dependency}'", exception, "dependency"
            )

        self.output.error(msg)
        return msg, code

    def handle_resource_error(
        self, resource_type: str, resource_name: str, exception: Exception
    ) -> Tuple[str, str]:
        """
        Handle errors related to system resources.

        Args:
            resource_type: Type of resource (memory, CPU, etc.)
            resource_name: Name or identifier of the resource
            exception: The exception that was raised

        Returns:
            Tuple containing (error_message, error_code)
        """
        if isinstance(exception, MemoryError):
            msg = f"Not enough memory to complete operation: {resource_name}"
            code = "resource:memory"
        elif "ResourceWarning" in str(type(exception)):
            msg = f"Resource warning for {resource_type}: {resource_name}"
            code = "resource:warning"
        else:
            return self._handle_generic(
                f"Resource error with {resource_type}: {resource_name}",
                exception,
                "resource",
            )

        self.output.error(msg)
        return msg, code

    def exit_if_critical(self, error_code: str, exit_code: int = 1) -> None:
        """
        Exit the program if the error is critical and exit_on_critical is True.

        Args:
            error_code: The error code returned from a handler
            exit_code: The exit code to use
        """
        critical_prefixes = ["config:", "dependency:", "resource:memory"]

        if self.exit_on_critical and any(
            error_code.startswith(prefix) for prefix in critical_prefixes
        ):
            self.output.error(f"Exiting due to critical error: {error_code}")
            sys.exit(exit_code)

    def with_error_handling(
        self,
        func: Callable,
        handler: Callable[[Exception], Tuple[str, str]],
        exit_on_error: bool = False,
    ) -> Callable:
        """
        Decorator factory to wrap a function with error handling.

        Args:
            func: The function to wrap
            handler: The error handler to use
            exit_on_error: Whether to exit on error

        Returns:
            Wrapped function with error handling
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                msg, code = handler(e)
                if exit_on_error:
                    self.output.error(f"Exiting due to error: {code}")
                    sys.exit(1)
                return None

        return wrapper


# Convenience functions for common operations


def handle_file_error(
    output: Output, path: Path, exception: Exception, operation: str = "access"
) -> Tuple[str, str]:
    """
    Convenience function for handling file operation errors.

    Args:
        output: Output utility for displaying messages
        path: The file that was being operated on
        exception: The exception that was raised
        operation: The operation being performed

    Returns:
        Tuple containing (error_message, error_code)
    """
    handler = ErrorHandler(output)
    return handler.handle_file_operation(path, exception, operation)


def handle_network_error(
    output: Output, resource: str, exception: Exception, operation: str = "access"
) -> Tuple[str, str]:
    """
    Convenience function for handling network operation errors.

    Args:
        output: Output utility for displaying messages
        resource: The resource being accessed
        exception: The exception that was raised
        operation: The operation being performed

    Returns:
        Tuple containing (error_message, error_code)
    """
    handler = ErrorHandler(output)
    return handler.handle_network_operation(resource, exception, operation)


def handle_config_error(
    output: Output, config_path: Union[str, Path], exception: Exception
) -> Tuple[str, str]:
    """
    Convenience function for handling configuration errors.

    Args:
        output: Output utility for displaying messages
        config_path: Path to the configuration file
        exception: The exception that was raised

    Returns:
        Tuple containing (error_message, error_code)
    """
    handler = ErrorHandler(output)
    return handler.handle_config_error(config_path, exception)
