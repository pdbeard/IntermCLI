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

import sys
import json
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error

# Optional enhancements
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.syntax import Syntax
    from rich.panel import Panel

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# TOML support
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

__version__ = "0.1.0"


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


def print_response(response, verbose=False, show_headers=True):
    """Print response in a readable format"""
    if HAS_RICH and console:
        print_response_rich(response, verbose, show_headers)
    else:
        print_response_simple(response, verbose, show_headers)


def print_response_rich(response, verbose=False, show_headers=True):
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
    if hasattr(response, "text"):
        body = response.text
        if body:
            try:
                # Try to format as JSON
                formatted = format_json(body)
                syntax = Syntax(formatted, "json", theme="monokai", line_numbers=False)
                console.print(Panel(syntax, title="Response Body"))
            except Exception:
                # Fall back to plain text
                console.print(Panel(body, title="Response Body"))


def print_response_simple(response, verbose=False, show_headers=True):
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
    if hasattr(response, "text"):
        body = response.text
        if body:
            print("Body:")
            try:
                formatted = format_json(body)
                print(formatted)
            except Exception:
                print(body)


def load_collection(collection_path=None):
    """Load a TOML collection file with robust fallback (user, legacy, source-tree)."""
    from pathlib import Path

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

        print(f"  {dep}: {status}{enhancement}")


def main():
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

    # Request behavior
    parser.add_argument(
        "-t", "--timeout", type=int, default=30, help="Request timeout in seconds"
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

    # Utility
    parser.add_argument(
        "--check-deps", action="store_true", help="Check optional dependency status"
    )
    parser.add_argument(
        "--version", action="version", version=f"test-endpoints {__version__}"
    )

    args = parser.parse_args()

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

    # Parse headers
    headers = {}
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
                timeout=args.timeout,
                verify=not args.no_verify,
            )
        else:
            # Use stdlib
            request_data = json_data if json_data else data
            response = make_request_simple(
                method=method,
                url=url,
                headers=headers,
                data=request_data,
                timeout=args.timeout,
            )

        # Print response
        print_response(response, args.verbose, not args.no_headers)

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
