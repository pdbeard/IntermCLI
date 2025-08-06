#!/usr/bin/env python3
"""
test-endpoints: Command-line API testing tool for developers who want a fast,
scriptable alternative to GUI tools like Postman. Test REST APIs, GraphQL endpoints,
and webhooks directly from your terminal.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    test-endpoints https://api.github.com/users/octocat
    test-endpoints POST https://httpbin.org/post --json '{"name": "test"}'
    test-endpoints GET https://api.example.com/data --header "Authorization: Bearer token123"
    test-endpoints --collection my-api --request "Get Users" --env dev
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict

# Ensure shared utilities are available
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
try:
    from shared.path_utils import require_shared_utilities

    require_shared_utilities()
except ImportError:
    # If even path_utils can't be imported, provide a fallback error
    print("Error: IntermCLI shared utilities not found.")
    print("Please make sure the IntermCLI suite is properly installed.")
    sys.exit(1)

# Import shared utilities
from shared.arg_parser import ArgumentParser
from shared.config_loader import ConfigLoader
from shared.enhancement_loader import EnhancementLoader
from shared.error_handler import ErrorHandler
from shared.network_utils import NetworkUtils
from shared.output import setup_tool_output

# Version
__version__ = "0.1.0"
TOOL_NAME = "test-endpoints"


# Optional enhancements
try:
    import requests as _requests  # noqa: F401

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from rich.console import Console

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# TOML support is handled by ConfigLoader from shared utilities


class SimpleResponse:
    """Simple response wrapper for urllib"""

    def __init__(self, response, url, start_time):
        self.status_code = response.getcode()
        self.headers = dict(response.headers)
        self.url = url
        self.text = response.read().decode("utf-8", errors="ignore")
        self.elapsed = time.time() - start_time

    def json(self):
        return json.loads(self.text)


def make_request_simple(
    method, url, headers=None, data=None, timeout=30, output=None, error_handler=None
):
    """Make HTTP request using urllib (stdlib only)"""
    headers = headers or {}

    # Prepare request
    if data and isinstance(data, dict):
        data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif data and isinstance(data, str):
        data = data.encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    start_time = time.time()
    try:
        response = urllib.request.urlopen(req, timeout=timeout)
        return SimpleResponse(response, url, start_time)
    except urllib.error.HTTPError as e:
        # Still return response for error status codes
        return SimpleResponse(e, url, start_time)
    except Exception as e:
        if error_handler:
            error_handler.handle_network_operation(url, e, "connect to")
        raise


def make_request_enhanced(
    method,
    url,
    headers=None,
    json_data=None,
    data=None,
    timeout=30,
    verify_ssl=True,
    output=None,
    error_handler=None,
):
    """Make an HTTP request using the requests library"""
    try:
        import requests

        kwargs = {
            "headers": headers or {},
            "timeout": timeout,
            "verify": verify_ssl,
            "allow_redirects": True,
        }

        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["data"] = data

        # Create a progress bar if output has the method
        if output and hasattr(output, "create_progress_bar"):
            with output.create_progress_bar(
                total=100, description=f"Requesting {method} {url}"
            ) as progress_bar:
                # Make the request
                start_time = time.time()

                # Update progress bar to show request in progress
                progress_bar.update(10)  # Show initial progress

                response = requests.request(method, url, **kwargs)

                # Update progress bar to show request completed
                progress_bar.update(90)  # Complete progress
        else:
            # Make the request without progress bar
            start_time = time.time()
            response = requests.request(method, url, **kwargs)

        response.elapsed = time.time() - start_time
        return response
    except Exception as e:
        if error_handler:
            msg, code = error_handler.handle_network_operation(url, e, "connect to")
        elif output:
            output.error(f"Request failed: {e}")
        raise


def make_request(
    method,
    url,
    headers=None,
    json_data=None,
    data=None,
    timeout=30,
    verify_ssl=True,
    output=None,
    error_handler=None,
):
    """
    Make an HTTP request using the best available method (NetworkUtils, requests, or urllib)

    Args:
        method: HTTP method (GET, POST, etc.)
        url: URL to request
        headers: Dictionary of headers
        json_data: JSON data for request body
        data: String or bytes data for request body
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        output: Output utility for messages
        error_handler: ErrorHandler for error handling

    Returns:
        Response object with status_code, headers, text, and elapsed properties
    """
    # Try to use shared NetworkUtils first (if available)
    try:
        # Initialize a NetworkUtils instance with our timeout
        network_utils = NetworkUtils(timeout=timeout)

        if hasattr(network_utils, "http_request"):
            if output:
                output.debug(f"Using shared NetworkUtils for {method} request to {url}")

            # Convert parameters to NetworkUtils format
            kwargs = {"headers": headers or {}, "verify": verify_ssl}

            if json_data:
                kwargs["json"] = json_data
            elif data:
                kwargs["data"] = data

            start_time = time.time()
            response = network_utils.http_request(method, url, **kwargs)
            response.elapsed = time.time() - start_time
            return response
    except (ImportError, AttributeError) as e:
        # Fall back to direct requests or urllib
        if output:
            output.debug(f"Falling back to direct request methods: {e}")

    # Fall back to requests or urllib
    if HAS_REQUESTS:
        return make_request_enhanced(
            method,
            url,
            headers,
            json_data,
            data,
            timeout,
            verify_ssl,
            output,
            error_handler,
        )
    else:
        # Combine json_data and data for urllib
        request_data = None
        if json_data:
            request_data = json_data
        elif data:
            request_data = data

        return make_request_simple(
            method, url, headers, request_data, timeout, output, error_handler
        )


def format_json(text):
    """Format JSON with proper indentation"""
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return text


def print_response(
    response,
    verbose=False,
    show_headers=True,
    output_format="auto",
    output=None,
    full_output=False,
):
    """Print response in a readable format based on the specified output format"""
    # Use provided output or fallback to direct printing
    has_output_utility = output is not None

    # First, check if we need to convert the response to another format
    response_body = getattr(response, "text", "")

    # Handle different output formats
    if output_format == "json" and response_body:
        try:
            # Try to parse and reformat as JSON regardless of the original format
            parsed = json.loads(response_body)
            response_body = json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If not valid JSON, keep original
            output_format = "text"
            if has_output_utility:
                output.warning("Response is not valid JSON, displaying as text")
            else:
                print("⚠️ Response is not valid JSON, displaying as text")
    elif output_format == "yaml" and response_body:
        try:
            # Convert to YAML if PyYAML is available
            try:
                import yaml

                # Try to parse as JSON first, then convert to YAML
                try:
                    parsed = json.loads(response_body)
                    response_body = yaml.dump(parsed, default_flow_style=False)
                except json.JSONDecodeError:
                    # If not JSON, try to load as YAML and redump (to pretty print)
                    parsed = yaml.safe_load(response_body)
                    response_body = yaml.dump(parsed, default_flow_style=False)
            except ImportError:
                if has_output_utility:
                    output.warning(
                        "YAML output format requires PyYAML: pip install pyyaml"
                    )
                else:
                    print("⚠️ YAML output format requires PyYAML: pip install pyyaml")
                output_format = "auto"  # Fallback to auto
        except Exception:
            output_format = "text"
            if has_output_utility:
                output.warning("Could not convert response to YAML, displaying as text")
            else:
                print("⚠️ Could not convert response to YAML, displaying as text")

    # Now decide how to display it
    if HAS_RICH and console and output_format != "text":
        print_response_rich(
            response, verbose, show_headers, response_body, None, full_output
        )
    else:
        print_response_simple(
            response, verbose, show_headers, response_body, None, full_output
        )


def print_response_rich(
    response,
    verbose=False,
    show_headers=True,
    formatted_body=None,
    output=None,
    full_output=False,
):
    """Print response using rich formatting"""
    # Use provided output or fallback to direct rich console
    if output and output.rich_console:
        rich_console = output.rich_console
    else:
        rich_console = console

    if not rich_console:
        print_response_simple(
            response, verbose, show_headers, formatted_body, output, full_output
        )
        return

    # Status line
    status_color = (
        "green"
        if 200 <= response.status_code < 300
        else "red" if response.status_code >= 400 else "yellow"
    )
    elapsed_ms = int(getattr(response, "elapsed", 0) * 1000)

    rich_console.print(f"[{status_color}]✅ {response.status_code}[/] ({elapsed_ms}ms)")

    # Headers
    if show_headers and hasattr(response, "headers"):
        from rich.table import Table

        headers_table = Table(title="Headers", show_header=False, box=None)
        headers_table.add_column("Key", style="cyan")
        headers_table.add_column("Value", style="white")

        for key, value in response.headers.items():
            headers_table.add_row(key, str(value))

        rich_console.print(headers_table)

    # Body
    if formatted_body is not None:
        body = formatted_body
    elif hasattr(response, "text"):
        body = response.text
    else:
        body = ""

    if body:
        display_body = body
        truncated = False
        if not full_output:
            MAX_BODY_LINES = 40
            MAX_LINE_LENGTH = 160
            try:
                parsed_json = json.loads(body)
                pretty = json.dumps(parsed_json, indent=2, ensure_ascii=False)
            except Exception:
                pretty = body
            lines = pretty.splitlines()
            if len(lines) > MAX_BODY_LINES:
                lines = lines[:MAX_BODY_LINES]
                truncated = True
            lines = [
                (
                    line
                    if len(line) <= MAX_LINE_LENGTH
                    else line[:MAX_LINE_LENGTH] + " ..."
                )
                for line in lines
            ]
            display_body = "\n".join(lines)
        try:
            from rich.panel import Panel
            from rich.syntax import Syntax

            # Detect if the body is JSON
            if display_body.strip().startswith(("{", "[")):
                syntax = Syntax(
                    display_body, "json", theme="monokai", line_numbers=False
                )
                rich_console.print(Panel(syntax, title="Response Body"))
            # Detect if the body is YAML
            elif (
                ":" in display_body and "\n" in display_body and "<" not in display_body
            ):
                syntax = Syntax(
                    display_body, "yaml", theme="monokai", line_numbers=False
                )
                rich_console.print(Panel(syntax, title="Response Body"))
            else:
                rich_console.print(Panel(display_body, title="Response Body"))
            if truncated:
                rich_console.print(
                    "[yellow]... (output truncated, showing first 40 lines)[/]"
                )
        except Exception:
            from rich.panel import Panel

            rich_console.print(Panel(display_body, title="Response Body"))
            if truncated:
                rich_console.print("... (output truncated, showing first 40 lines)")


def print_response_simple(
    response,
    verbose=False,
    show_headers=True,
    formatted_body=None,
    output=None,
    full_output=False,
):
    """Print response using simple text formatting"""
    status_emoji = (
        "✅"
        if 200 <= response.status_code < 300
        else "❌" if response.status_code >= 400 else "⚠️"
    )
    elapsed_ms = int(getattr(response, "elapsed", 0) * 1000)

    print(f"{status_emoji} {response.status_code} ({elapsed_ms}ms)")
    print()

    # Headers
    if show_headers and hasattr(response, "headers"):
        print("Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()

    # Body
    if formatted_body is not None:
        body = formatted_body
    elif hasattr(response, "text"):
        body = response.text
    else:
        body = ""

    if body:
        print("Body:")
        MAX_BODY_LINES = 40
        MAX_LINE_LENGTH = 160
        try:
            parsed_json = json.loads(body)
            pretty = json.dumps(parsed_json, indent=2, ensure_ascii=False)
        except Exception:
            pretty = body
        lines = pretty.splitlines()
        truncated = False
        if not full_output and len(lines) > MAX_BODY_LINES:
            lines = lines[:MAX_BODY_LINES]
            truncated = True
        if not full_output:
            lines = [
                (
                    line
                    if len(line) <= MAX_LINE_LENGTH
                    else line[:MAX_LINE_LENGTH] + " ..."
                )
                for line in lines
            ]
        for line in lines:
            print(line)
        if truncated:
            print(f"... (output truncated, showing first {MAX_BODY_LINES} lines)")


def load_config(config_path=None, output=None) -> Dict[str, Any]:
    """
    Load TOML config using the shared ConfigLoader utility.
    Args:
        config_path (str or Path, optional): Path to a config file. If not provided, tries user and source-tree defaults.
        output (Output, optional): Output utility for error handling
    Returns:
        dict: Configuration dictionary for HTTP requests and defaults.
    """
    # Default configuration
    default_config = {
        "general": {
            "timeout": 30,
            "max_redirects": 5,
            "verify_ssl": True,
            "verbose": False,
            "follow_redirects": True,
            "output_format": "auto",
        },
        "default_headers": {
            "User-Agent": f"intermCLI/{TOOL_NAME}",
            "Accept": "*/*",
        },
    }

    # Use the shared ConfigLoader
    config_loader = ConfigLoader(TOOL_NAME)

    # Add the specific config file if provided
    if config_path:
        config_loader.add_config_file(config_path)

    # Load the configuration with proper precedence
    try:
        config = config_loader.load_config()
        # Merge with defaults for backward compatibility
        for section in default_config:
            if section not in config:
                config[section] = default_config[section]
            elif isinstance(default_config[section], dict):
                for key, value in default_config[section].items():
                    if key not in config[section]:
                        config[section][key] = value
        return config
    except Exception as e:
        if output:
            error_handler = ErrorHandler(output, exit_on_critical=True)
            msg, code = error_handler.handle_config_error(
                config_path or "default config", e
            )
            # This will exit if exit_on_critical is True and the error is critical
            error_handler.exit_if_critical(code)

        # Otherwise return the default config
        return default_config


def load_collection(collection_path=None, output=None):
    """
    Load a collection configuration file using the shared ConfigLoader.

    Args:
        collection_path (str or Path, optional): Path to a collection file
        output (Output, optional): Output utility for error handling

    Returns:
        dict: Collection configuration or None if not found
    """
    # Create a separate config loader for collections
    collection_loader = ConfigLoader(TOOL_NAME, section_name="collections")

    # Add the specific collection file if provided
    if collection_path:
        collection_loader.add_config_file(collection_path)

    try:
        collection_config = collection_loader.load_config()
        if output:
            output.info("Loaded collection configuration")
        return collection_config
    except Exception as e:
        if output:
            error_handler = ErrorHandler(output)
            msg, code = error_handler.handle_config_error(
                collection_path or "default collection", e
            )
            output.warning("No collection config found, using defaults if any.")
        return None


def substitute_variables(text, variables):
    """Simple variable substitution using {{variable}} syntax"""
    if not isinstance(text, str):
        return text

    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))

    return text


def check_dependencies(output=None):
    """Check status of optional dependencies using shared EnhancementLoader"""
    enhancer = EnhancementLoader(TOOL_NAME)
    enhancer.check_dependency("requests", "Enhanced HTTP features")
    enhancer.check_dependency("rich", "Colorized output")
    enhancer.check_dependency("pyyaml", "YAML response formatting")

    if output:
        # Set output before printing status
        enhancer.output = output

        # Custom display using new output methods if available
        if hasattr(output, "print_key_value_section"):
            # Create a dictionary of dependencies with their status
            dependencies = {
                key: "Available" if value else "Missing"
                for key, value in enhancer.dependencies.items()
            }

            output.print_key_value_section(
                f"Optional Dependencies for {TOOL_NAME}", dependencies
            )

            # Create a list of missing dependencies for installation instructions
            missing = enhancer.get_missing_dependencies()
            if missing:
                output.info("\nTo enable all features, install missing dependencies:")

                if hasattr(output, "print_list"):
                    # Display as a list with pip install commands
                    install_commands = [f"pip install {dep}" for dep in missing]
                    output.print_list("Install Commands", install_commands)
                else:
                    # Fallback to simple output
                    output.info(f"  pip install {' '.join(missing)}")
        else:
            # Fallback to original method
            enhancer.print_status()
    else:
        enhancer.print_status()

    if not HAS_REQUESTS and output:
        output.warning(
            "Without 'requests', only basic HTTP features will be available."
        )
        output.info("Install with: pip install requests")
    elif not HAS_REQUESTS:
        print("\nNote: Without 'requests', only basic HTTP features will be available.")
        print("      Install with: pip install requests")

    # Return list of missing dependencies
    return enhancer.get_missing_dependencies()


def main():
    # Initialize shared output utility
    output = setup_tool_output(tool_name=TOOL_NAME, log_level="INFO", use_rich=True)
    error_handler = ErrorHandler(output)

    # Display tool banner
    output.banner(
        TOOL_NAME,
        __version__,
        {
            "Description": "Command-line API testing tool - fast, scriptable alternative to Postman"
        },
    )

    # Load configuration first
    config = load_config(output=output)
    general_config = config.get("general", {})
    default_headers = config.get("default_headers", {})

    # Setup argument parser using the shared utility
    parser = ArgumentParser(
        TOOL_NAME,
        "Command-line API testing tool - fast, scriptable alternative to Postman",
        epilog="Example: test-endpoints GET https://httpbin.org/json",
        version=__version__,
    )

    # Add common arguments
    parser.add_common_arguments()

    # Basic request arguments
    parser.add_positional_argument(
        "method_or_url",
        "HTTP method or URL (if method not specified, defaults to GET)",
        nargs="?",
    )
    parser.add_positional_argument("url", "URL to request", nargs="?")

    # Request options
    parser.parser.add_argument(
        "-X", "--method", help="HTTP method (GET, POST, PUT, DELETE, etc.)"
    )
    parser.parser.add_argument(
        "-H", "--header", action="append", help="Add header (format: 'Key: Value')"
    )
    parser.parser.add_argument("-d", "--data", help="Request body data")
    parser.parser.add_argument("-j", "--json", help="JSON request body")
    parser.parser.add_argument(
        "-p", "--param", action="append", help="Query parameter (format: 'key=value')"
    )

    # Output options
    output_group = parser.parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--no-headers", action="store_true", help="Don't show response headers"
    )
    output_group.add_argument("-o", "--output", help="Save response to file")
    output_group.add_argument(
        "--format",
        choices=["auto", "json", "yaml", "text"],
        help="Output format (auto, json, yaml, text)",
    )
    output_group.add_argument(
        "--full-output",
        action="store_true",
        help="Show the full response body (disable truncation in output)",
    )

    # Request behavior
    request_group = parser.parser.add_argument_group("Request Options")
    request_group.add_argument(
        "-t",
        "--timeout",
        type=int,
        help=f"Request timeout in seconds (default: {general_config.get('timeout', 30)})",
    )
    request_group.add_argument(
        "--no-verify", action="store_true", help="Disable SSL verification"
    )
    request_group.add_argument("--follow", action="store_true", help="Follow redirects")

    # Collections and environments
    collection_group = parser.parser.add_argument_group("Collections")
    collection_group.add_argument(
        "--collection", help="Collection name or path to TOML file"
    )
    collection_group.add_argument("--request", help="Request name from collection")
    collection_group.add_argument("--env", help="Environment name")
    collection_group.add_argument(
        "--set", action="append", help="Set variable (format: 'key=value')"
    )

    # The --config argument is already added by add_common_arguments()

    # Utility
    # The --check-deps argument is already added by add_common_arguments()

    args = parser.parser.parse_args()

    # Apply verbosity setting to output
    output.verbose = args.verbose

    # If config file specified, reload with that file
    if args.config:
        config = load_config(args.config, output=output)
        general_config = config.get("general", {})
        default_headers = config.get("default_headers", {})

    # Check dependencies and exit
    if args.check_deps:
        check_dependencies(output=output)
        return

    # Parse method and URL
    if args.url:
        method = args.method_or_url.upper() if args.method_or_url else "GET"
        url = args.url
    elif args.method_or_url:
        # Single argument - assume it's a URL and default to GET
        method = args.method.upper() if args.method else "GET"
        url = args.method_or_url
    else:
        parser.parser.print_help()
        return

    # Validate URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Set up headers starting with defaults from config
    headers = default_headers.copy()

    # Add headers from command line (overriding defaults)
    if args.header:
        for header in args.header:
            if ":" in header:
                key, value = header.split(":", 1)
                headers[key.strip()] = value.strip()

    # Parse query parameters
    if args.param:
        params = []
        for param in args.param:
            if "=" in param:
                params.append(param)
        if params:
            separator = "&" if "?" in url else "?"
            url += separator + "&".join(params)

    # Parse request body
    data = None
    json_data = None

    if args.json:
        try:
            json_data = json.loads(args.json)
        except json.JSONDecodeError as e:
            error_msg, error_code = error_handler.handle_value_error(
                "JSON data", e, "parse"
            )
            output.error(f"Invalid JSON: {e}")
            return
    elif args.data:
        data = args.data

    # Get timeout from args or config
    timeout = (
        args.timeout if args.timeout is not None else general_config.get("timeout", 30)
    )

    # Get SSL verification setting
    verify_ssl = (
        not args.no_verify if args.no_verify else general_config.get("verify_ssl", True)
    )

    # Get output format
    output_format = (
        args.format if args.format else general_config.get("output_format", "auto")
    )

    # Make request
    output.info(f"🌐 {method} {url}")

    try:
        response = make_request(
            method=method,
            url=url,
            headers=headers,
            json_data=json_data,
            data=data,
            timeout=timeout,
            verify_ssl=verify_ssl,
            output=output,
            error_handler=error_handler,
        )

        # Print response (always use classic output, not output utility)
        print_response(
            response,
            args.verbose,
            not args.no_headers,
            output_format,
            None,
            args.full_output,
        )

        # Save to file if requested
        if args.output:
            try:
                with open(args.output, "w") as f:
                    f.write(response.text)
                output.success(f"Response saved to {args.output}")
            except Exception as e:
                error_handler.handle_file_operation(
                    Path(args.output), e, operation="write"
                )

    except Exception as e:
        error_handler.handle_network_operation(url, e, "connect to")
        sys.exit(1)


if __name__ == "__main__":
    main()
