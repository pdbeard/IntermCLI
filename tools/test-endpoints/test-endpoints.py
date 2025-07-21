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

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict

# Version
__version__ = "0.1.0"

# Optional enhancements
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# TOML support
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python
    except ImportError:
        tomllib = None


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


def make_request_simple(method, url, headers=None, data=None, timeout=30):
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


def make_request_enhanced(
    method, url, headers=None, json_data=None, data=None, timeout=30, verify=True
):
    """Make HTTP request using requests library"""
    start_time = time.time()

    kwargs = {"timeout": timeout, "verify": verify, "headers": headers or {}}

    if json_data:
        kwargs["json"] = json_data
    elif data:
        kwargs["data"] = data

    response = requests.request(method, url, **kwargs)
    response.elapsed = time.time() - start_time
    return response


def format_json(text):
    """Format JSON with proper indentation"""
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return text


def print_response(response, verbose=False, show_headers=True, output_format="auto"):
    """Print response in a readable format based on the specified output format"""
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
                print("⚠️ YAML output format requires PyYAML: pip install pyyaml")
                output_format = "auto"  # Fallback to auto
        except Exception:
            output_format = "text"
            print("⚠️ Could not convert response to YAML, displaying as text")

    # Now decide how to display it
    if HAS_RICH and console and output_format != "text":
        print_response_rich(response, verbose, show_headers, response_body)
    else:
        print_response_simple(response, verbose, show_headers, response_body)


def print_response_rich(
    response, verbose=False, show_headers=True, formatted_body=None
):
    """Print response using rich formatting"""
    # Status line
    status_color = (
        "green"
        if 200 <= response.status_code < 300
        else "red" if response.status_code >= 400 else "yellow"
    )
    elapsed_ms = int(getattr(response, "elapsed", 0) * 1000)

    console.print(f"[{status_color}]✅ {response.status_code}[/] ({elapsed_ms}ms)")

    # Headers
    if show_headers and hasattr(response, "headers"):
        headers_table = Table(title="Headers", show_header=False, box=None)
        headers_table.add_column("Key", style="cyan")
        headers_table.add_column("Value", style="white")

        for key, value in response.headers.items():
            headers_table.add_row(key, str(value))

        console.print(headers_table)

    # Body
    if formatted_body is not None:
        body = formatted_body
    elif hasattr(response, "text"):
        body = response.text
    else:
        body = ""

    if body:
        try:
            # Detect if the body is JSON
            if body.strip().startswith(("{", "[")):
                syntax = Syntax(body, "json", theme="monokai", line_numbers=False)
                console.print(Panel(syntax, title="Response Body"))
            # Detect if the body is YAML
            elif ":" in body and "\n" in body and "<" not in body:
                syntax = Syntax(body, "yaml", theme="monokai", line_numbers=False)
                console.print(Panel(syntax, title="Response Body"))
            else:
                console.print(Panel(body, title="Response Body"))
        except Exception:
            # Fall back to plain text
            console.print(Panel(body, title="Response Body"))


def print_response_simple(
    response, verbose=False, show_headers=True, formatted_body=None
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
        # Try to format as JSON for backward compatibility with tests
        try:
            if body.strip().startswith(("{", "[")):
                formatted = format_json(body)
                print(formatted)
            else:
                print(body)
        except Exception:
            print(body)


def load_config(config_path=None) -> Dict[str, Any]:
    """Load configuration with proper precedence.

    Searches for configuration in the following locations (highest precedence first):
    1. Specified path (if provided)
    2. User tool-specific config (~/.config/intermcli/test-endpoints.toml)
    3. User global config (~/.config/intermcli/config.toml)
    4. Tool default config (./config/defaults.toml)
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
            "User-Agent": "intermCLI/test-endpoints",
            "Accept": "*/*",
        },
    }

    if not tomllib:
        print("❌ TOML support not available. Install tomli: pip install tomli")
        return default_config

    # Define config file paths in precedence order (lowest to highest)
    script_dir = Path(__file__).parent
    source_config_file = script_dir / "config" / "defaults.toml"
    user_config_dir = Path.home() / ".config" / "intermcli"
    user_global_config = user_config_dir / "config.toml"
    user_tool_config = user_config_dir / "test-endpoints.toml"

    config_paths = [
        source_config_file,
        user_global_config,
        user_tool_config,
    ]

    # Add specific path if provided
    if config_path:
        config_paths.append(Path(config_path))

    # Try loading each config file in precedence order
    config = default_config
    config_loaded = None

    for path in config_paths:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    file_config = tomllib.load(f)

                # Deep update the configuration
                deep_update(config, file_config)
                config_loaded = path
            except Exception as e:
                print(f"⚠️ Warning: Failed to load config from {path}: {e}")

    if config_loaded:
        print(f"ℹ️ Using configuration from: {config_loaded}")
    else:
        print("ℹ️ Using default configuration")

    return config


def deep_update(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """Recursively update a dictionary with another dictionary."""
    for key, value in update_dict.items():
        if (
            isinstance(value, dict)
            and key in base_dict
            and isinstance(base_dict[key], dict)
        ):
            deep_update(base_dict[key], value)
        else:
            base_dict[key] = value


def load_collection(collection_path=None):
    """Load a TOML collection file with robust fallback (user, legacy, source-tree)."""
    script_dir = Path(__file__).parent
    source_config_file = script_dir / "config" / "defaults.toml"
    user_config_dir = Path.home() / ".config" / "intermcli"
    user_config_file = user_config_dir / "test-endpoints.toml"
    legacy_user_config_file = user_config_dir / "config.toml"

    config_loaded = None
    config_paths = []
    if collection_path:
        config_paths.append(collection_path)
    config_paths.extend(
        [
            str(user_config_file),
            str(legacy_user_config_file),
            str(source_config_file),
        ]
    )

    if not tomllib:
        print("❌ TOML support not available. Install tomli: pip install tomli")
        return None

    for path in config_paths:
        p = Path(path)
        if p.exists():
            try:
                with open(p, "rb") as f:
                    file_config = tomllib.load(f)
                config_loaded = str(p)
            except Exception as e:
                print(f"❌ Failed to load collection: {path}: {e}")
                file_config = None
            break  # Use the first config found
        else:
            file_config = None

    if config_loaded:
        print(f"ℹ️  Loaded collection config: {config_loaded}")
    else:
        print("ℹ️  No collection config found, using defaults if any.")
    return file_config


def substitute_variables(text, variables):
    """Simple variable substitution using {{variable}} syntax"""
    if not isinstance(text, str):
        return text

    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))

    return text


def check_dependencies():
    """Check status of optional dependencies"""
    deps = {
        "requests": HAS_REQUESTS,
        "rich": HAS_RICH,
        "tomli/tomllib": tomllib is not None,
    }

    # Check for PyYAML
    import importlib.util

    deps["pyyaml"] = importlib.util.find_spec("yaml") is not None

    print("🔍 Dependency Status:")
    for dep, available in deps.items():
        status = "✅ Available" if available else "❌ Not installed"
        enhancement = ""
        if dep == "requests":
            enhancement = " (Enhanced HTTP features)"
        elif dep == "rich":
            enhancement = " (Colorized output)"
        elif dep == "tomli/tomllib":
            enhancement = " (Collection support)"
        elif dep == "pyyaml":
            enhancement = " (YAML response formatting)"

        print(f"  {dep}: {status}{enhancement}")

    # Provide installation hint for missing dependencies
    missing = [dep for dep, available in deps.items() if not available]
    if missing:
        print("\nTo enable all features, install missing dependencies:")
        install_cmd = "pip install "
        for dep in missing:
            if dep == "tomli/tomllib":
                install_cmd += "tomli "
            elif dep == "pyyaml":
                install_cmd += "pyyaml "
            else:
                install_cmd += f"{dep} "
        print(f"  {install_cmd.strip()}")


def main():
    # Load configuration first
    config = load_config()
    general_config = config.get("general", {})
    default_headers = config.get("default_headers", {})

    parser = argparse.ArgumentParser(
        description="Command-line API testing tool - fast, scriptable alternative to Postman",
        epilog="Example: test-endpoints GET https://httpbin.org/json",
    )

    # Basic request arguments
    parser.add_argument(
        "method_or_url",
        nargs="?",
        help="HTTP method or URL (if method not specified, defaults to GET)",
    )
    parser.add_argument("url", nargs="?", help="URL to request")

    # Request options
    parser.add_argument(
        "-X", "--method", help="HTTP method (GET, POST, PUT, DELETE, etc.)"
    )
    parser.add_argument(
        "-H", "--header", action="append", help="Add header (format: 'Key: Value')"
    )
    parser.add_argument("-d", "--data", help="Request body data")
    parser.add_argument("-j", "--json", help="JSON request body")
    parser.add_argument(
        "-p", "--param", action="append", help="Query parameter (format: 'key=value')"
    )

    # Output options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--no-headers", action="store_true", help="Don't show response headers"
    )
    parser.add_argument("-o", "--output", help="Save response to file")
    parser.add_argument(
        "--format",
        choices=["auto", "json", "yaml", "text"],
        help="Output format (auto, json, yaml, text)",
    )

    # Request behavior
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help=f"Request timeout in seconds (default: {general_config.get('timeout', 30)})",
    )
    parser.add_argument(
        "--no-verify", action="store_true", help="Disable SSL verification"
    )
    parser.add_argument("--follow", action="store_true", help="Follow redirects")

    # Collections and environments
    parser.add_argument("--collection", help="Collection name or path to TOML file")
    parser.add_argument("--request", help="Request name from collection")
    parser.add_argument("--env", help="Environment name")
    parser.add_argument(
        "--set", action="append", help="Set variable (format: 'key=value')"
    )
    parser.add_argument("--config", help="Path to specific config file")

    # Utility
    parser.add_argument(
        "--check-deps", action="store_true", help="Check optional dependency status"
    )
    parser.add_argument(
        "--version", action="version", version=f"test-endpoints {__version__}"
    )

    args = parser.parse_args()

    # If config file specified, reload with that file
    if args.config:
        config = load_config(args.config)
        general_config = config.get("general", {})
        default_headers = config.get("default_headers", {})

    # Check dependencies and exit
    if args.check_deps:
        check_dependencies()
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
        parser.print_help()
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
            print(f"❌ Invalid JSON: {e}")
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

    # Get verbose setting
    verbose = args.verbose if args.verbose else general_config.get("verbose", False)

    # Make request
    print(f"🌐 {method} {url}")

    try:
        if HAS_REQUESTS:
            response = make_request_enhanced(
                method=method,
                url=url,
                headers=headers,
                json_data=json_data,
                data=data,
                timeout=timeout,
                verify=verify_ssl,
            )
        else:
            # Use stdlib
            request_data = json_data if json_data else data
            response = make_request_simple(
                method=method,
                url=url,
                headers=headers,
                data=request_data,
                timeout=timeout,
            )

        # Print response
        print_response(response, verbose, not args.no_headers, output_format)

        # Save to file if requested
        if args.output:
            with open(args.output, "w") as f:
                f.write(response.text)
            print(f"\n💾 Response saved to {args.output}")

    except Exception as e:
        print(f"❌ Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
