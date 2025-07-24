#!/usr/bin/env python3
"""
scan-ports: Scan local or remote hosts for open ports and detect running services.
Supports configurable port lists, service detection, and both basic and enhanced detection modes.

Part of the IntermCLI suite – interactive terminal utilities for developers and power users.

Example usage:
    scan-ports localhost
    scan-ports 192.168.1.1
    scan-ports --list web
    scan-ports -p 8080
    scan-ports --show-lists
    scan-ports --check-deps
"""

import argparse  # Still needed for type annotations
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypeVar

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
from shared.error_handler import ErrorHandler
from shared.network_utils import create_network_utils
from shared.output import setup_tool_output

# Check for optional dependencies (test compatibility)
HAS_RICH = False
HAS_REQUESTS = False
HAS_URLLIB3 = False
HAS_SSL = False


# Optional dependencies are checked in shared.network_utils, so these imports are not needed here.

# Optional rich-specific imports
try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    HAS_RICH = True
    console = Console()  # type: ignore
except ImportError:
    HAS_RICH = False
    console = None  # type: ignore

T = TypeVar("T")  # Define a generic type variable for futures

__version__ = "0.1.0"
TOOL_NAME = "scan-ports"

# These will be initialized in main()
output = None
error_handler = None
config_loader = None
network_utils = None


def check_optional_dependencies() -> Tuple[Dict[str, bool], List[str]]:
    """Check which optional dependencies are available"""
    global HAS_REQUESTS, HAS_URLLIB3, HAS_SSL, HAS_RICH

    # Make sure network_utils is initialized
    if network_utils is None:
        return {
            "requests": False,
            "urllib3": False,
            "ssl": False,
            "rich": HAS_RICH,
            "tomllib": False,
        }, ["requests", "urllib3", "ssl", "tomllib"]

    # Update global flags based on network_utils
    HAS_REQUESTS = network_utils.has_requests
    HAS_URLLIB3 = network_utils.has_urllib3
    HAS_SSL = network_utils.has_ssl

    # Use network_utils dependency checking plus rich
    deps = {
        "requests": HAS_REQUESTS,
        "urllib3": HAS_URLLIB3,
        "ssl": HAS_SSL,
        "rich": HAS_RICH,
        "tomllib": config_loader.has_toml if config_loader else False,
    }

    missing = [name for name, available in deps.items() if not available]
    return deps, missing


def print_dependency_status(verbose: bool = False) -> None:
    """Print status of optional dependencies"""
    deps, missing = check_optional_dependencies()

    if verbose:
        output.info("Optional Dependencies Status:")
        for name, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            output.info(f"{name:10}: {status}")

        if missing:
            if "tomllib" in missing:
                output.info("For TOML support on Python < 3.11: pip3 install tomli")
            other_missing = [m for m in missing if m != "tomllib"]
            if other_missing:
                output.info(
                    f"To enable enhanced service detection: pip3 install {' '.join(other_missing)}"
                )
        output.blank()


def load_port_config() -> Dict[str, Any]:
    """Load port configuration from TOML file"""
    script_dir = Path(__file__).parent
    default_config_path = script_dir / "config" / "ports.toml"

    # Default fallback config
    default_config = {
        "port_lists": {
            "common": {
                "description": "Basic common ports",
                "ports": {
                    "22": "SSH",
                    "80": "HTTP",
                    "443": "HTTPS",
                    "3000": "Node.js Dev",
                    "5432": "PostgreSQL",
                },
            }
        }
    }

    try:
        # Set the default configuration
        config_loader.config = default_config

        # Add the specific ports.toml file to the config loader
        if default_config_path.exists():
            config_loader.add_config_file(default_config_path)

        # Load configuration through shared ConfigLoader
        config = config_loader.load_config()

        # If no port lists found in config, use default
        if "port_lists" not in config:
            output.warning("No port configuration found, using default port list.")
            return default_config

        return config
    except Exception as e:
        error_msg, error_code = error_handler.handle_config_error(
            "loading port configuration", e
        )
        output.warning(f"Error {error_code}: {error_msg}")
        output.info("Using default port list")
        return default_config


def log_separator(length: int = 60) -> None:
    """Print a separator line for console output"""
    output.separator(char="=", length=length)


def log_blank() -> None:
    """Print a blank line for console output"""
    output.blank()


def list_available_port_lists() -> None:
    """Display all available port lists from configuration"""
    config = load_port_config()

    output.info("Available Port Lists:")
    output.separator()

    for list_name, details in config["port_lists"].items():
        description = details.get("description", "No description")
        ports = details.get("ports", {})

        output.info(f"\n🏷️  {list_name.upper()}")
        output.info(f"   Description: {description}")
        output.info(f"   Ports: {len(ports)} defined")

        # Show first few ports as preview
        port_preview = list(ports.items())[:5]
        for port, service in port_preview:
            output.info(f"   • {port}: {service}")

        if len(ports) > 5:
            output.info(f"   ... and {len(ports) - 5} more")

    output.blank()
    output.separator()
    output.info("Usage: scan-ports -l <list_name> or scan-ports -l <list1>,<list2>")
    output.info("Example: scan-ports -l web,database")


def get_ports_from_lists(
    list_names: List[str], config: Dict[str, Any]
) -> Dict[int, str]:
    """Get ports from specified lists, or all if 'all' is specified"""
    ports: Dict[int, str] = {}
    available_lists: List[str] = list(config["port_lists"].keys())

    # If 'all' is in the list, combine all ports from all lists
    if any(name.strip().lower() == "all" for name in list_names):
        for list_name in available_lists:
            list_ports = config["port_lists"][list_name]["ports"]
            for port_str, service in list_ports.items():
                port = int(port_str)
                if port not in ports:
                    ports[port] = service
        return ports

    for list_name in list_names:
        list_name = list_name.strip().lower()
        if list_name in config["port_lists"]:
            list_ports = config["port_lists"][list_name]["ports"]
            for port_str, service in list_ports.items():
                port = int(port_str)
                if port not in ports:
                    ports[port] = service
        else:
            output.warning(f"Port list '{list_name}' not found")
            output.info(f"Available lists: {', '.join(available_lists)}")

    return ports


def check_port(host: str, port: int, timeout: float = 3) -> bool:
    """Check if a specific port is open using NetworkUtils"""
    try:
        # Use shared NetworkUtils
        network_utils.timeout = timeout
        return network_utils.check_port(host, port)
    except Exception as e:
        output.debug(f"Error checking port {port}: {e}")
        return False


def detect_service_banner(host: str, port: int, timeout: float = 3) -> Optional[str]:
    """Detect service banner using NetworkUtils"""
    try:
        # Use shared NetworkUtils
        network_utils.timeout = timeout
        return network_utils.detect_service_banner(host, port)
    except Exception as e:
        output.debug(f"Error detecting banner on port {port}: {e}")
        return None


def detect_http_service(
    host: str, port: int, timeout: float = 5
) -> Optional[Dict[str, Any]]:
    """Detect HTTP service using NetworkUtils"""
    try:
        # Use shared NetworkUtils
        network_utils.timeout = timeout
        result = network_utils.detect_http_service(host, port)

        if result:
            # Extract common fields to ensure consistent return format
            service_info = {
                "protocol": result.get("protocol", "http"),
                "status_code": result.get("status_code", 0),
                "server": result.get("server", "Unknown"),
                "title": result.get("title"),
                "framework": None,
                "redirect": result.get("redirect"),
            }

            # Add framework detection based on server and content
            if "server" in result:
                server_lower = result["server"].lower()
                if "nginx" in server_lower:
                    service_info["framework"] = "Nginx"
                elif "apache" in server_lower:
                    service_info["framework"] = "Apache"
                elif "express" in server_lower:
                    service_info["framework"] = "Express.js"

            return service_info
        return None
    except Exception as e:
        output.debug(f"Error detecting HTTP service on port {port}: {e}")
        return None


def detect_database_service(host: str, port: int, timeout: float = 3) -> Optional[str]:
    """Enhanced database detection with version probing"""
    database_signatures = {
        3306: "MySQL/MariaDB",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        9200: "Elasticsearch",
        5984: "CouchDB",
        8086: "InfluxDB",
    }

    # First try to get a service banner
    banner = detect_service_banner(host, port, timeout)

    if banner:
        banner_lower = banner.lower()
        if port == 6379 and "redis" in banner_lower:
            version_match = re.search(r"redis_version:([^\r\n]+)", banner)
            if version_match:
                return f"Redis {version_match.group(1)}"
        elif port == 9200 and "elasticsearch" in banner_lower:
            version_match = re.search(r'"number"\s*:\s*"([^"]+)"', banner)
            if version_match:
                return f"Elasticsearch {version_match.group(1)}"
        elif port == 3306 and "mysql" in banner_lower:
            return "MySQL" + (
                " " + banner.split(" ")[1] if len(banner.split(" ")) > 1 else ""
            )
        elif port == 5432 and "postgres" in banner_lower:
            return "PostgreSQL"

    # If no banner detected, use port-based detection
    return database_signatures.get(port)


def detect_ssh_service(host: str, port: int, timeout: float = 3) -> Optional[str]:
    """Detect SSH service version"""
    banner = detect_service_banner(host, port, timeout)
    if banner and banner.startswith("SSH"):
        return banner.strip()
    return "SSH" if port == 22 else None


def create_empty_service_result() -> Dict[str, Any]:
    """Create an empty service detection result for error cases"""
    return {
        "service": "Unknown",
        "version": "",
        "confidence": "low",
        "method": "basic",
        "details": {},
    }


def comprehensive_service_detection(
    host: str, port: int, timeout: float = 3
) -> Dict[str, Any]:
    """
    Comprehensive service detection combining multiple detection methods.
    Uses the most appropriate detection method based on port and available dependencies.

    Args:
        host: Target hostname or IP
        port: Port number to check
        timeout: Connection timeout in seconds

    Returns:
        Dictionary with service details including:
        - service: Service name
        - version: Version string if detected
        - confidence: Detection confidence (high, medium, low)
        - method: Detection method used (basic, enhanced)
        - details: Additional service details
    """
    # Common service port mapping as fallback
    common_ports = {
        22: "SSH",
        80: "HTTP",
        443: "HTTPS",
        21: "FTP",
        25: "SMTP",
        110: "POP3",
        143: "IMAP",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        27017: "MongoDB",
        9200: "Elasticsearch",
        9000: "SonarQube",
        8080: "HTTP-Alt",
        8443: "HTTPS-Alt",
        3000: "Node.js/React",
        3001: "Node.js Alt",
        8000: "Django/Python",
    }

    # Default result structure
    result: Dict[str, Any] = {
        "service": common_ports.get(port, "Unknown"),
        "version": None,
        "confidence": "low",
        "method": "basic",
        "details": {},
    }

    # Try SSH detection for port 22 or if port is likely SSH
    if port == 22 or (20 <= port <= 30):
        ssh_service = detect_ssh_service(host, port, timeout)
        if ssh_service:
            result["service"] = "SSH"
            result["version"] = ssh_service
            result["confidence"] = "high"
            return result

    # Try HTTP detection for common web ports
    if port in [80, 443, 8000, 8080, 8443, 3000, 3001, 5000, 8888, 9000]:
        # Normal detection
        http_info = detect_http_service(host, port, timeout)
        if http_info:
            # Determine the service name
            if http_info.get("framework"):
                service_name = http_info["framework"]
            elif http_info.get("server") and http_info["server"] != "Unknown":
                service_name = http_info["server"].split("/")[0]
            else:
                service_name = "HTTP" if http_info["protocol"] == "http" else "HTTPS"

            # Common web applications
            if port == 8000:
                service_name = "Django/Python"

            # Build the result
            result["service"] = service_name
            result["version"] = http_info.get("server", "").replace(
                service_name + "/", ""
            )
            result["confidence"] = "high"
            result["method"] = "enhanced" if network_utils.has_requests else "basic"
            # Make a copy of the dict to avoid type errors
            if http_info:
                result["details"] = dict(http_info)
            return result

    # Try database detection for common database ports
    if port in [3306, 5432, 6379, 27017, 9200, 5984, 8086]:
        # Normal detection
        db_info = detect_database_service(host, port, timeout)
        if db_info:
            # Split service name and version if present
            if " " in db_info:
                service, version = db_info.split(" ", 1)
                result["service"] = service
                result["version"] = version
            else:
                result["service"] = db_info

            result["confidence"] = "medium"
            return result

    # If we got here, try to get any banner
    banner = detect_service_banner(host, port, timeout)
    if banner:
        # Try to extract service info from banner
        lines = banner.splitlines()
        first_line = lines[0] if lines else banner[:50]

        # Look for common service identifiers in banner
        known_services = {
            "ssh": "SSH",
            "http": "HTTP",
            "ftp": "FTP",
            "smtp": "SMTP",
            "pop3": "POP3",
            "imap": "IMAP",
            "mysql": "MySQL",
            "postgresql": "PostgreSQL",
            "redis": "Redis",
            "mongodb": "MongoDB",
            "elastic": "Elasticsearch",
        }

        banner_lower = first_line.lower()
        for keyword, service_name in known_services.items():
            if keyword in banner_lower:
                result["service"] = service_name
                # Try to extract version
                version_match = re.search(r"[\d\.]+", first_line)
                if version_match:
                    result["version"] = version_match.group(0)
                result["confidence"] = "medium"
                return result

        # If no known service identified, use the first line as the service
        result["service"] = first_line[:30]
        result["confidence"] = "low"

    return result


def handle_list_scan(args: argparse.Namespace, detect_services: bool) -> None:
    """Handle scanning of ports from specific lists"""
    config = load_port_config()
    list_names = [name.strip() for name in args.list.split(",")]
    ports = get_ports_from_lists(list_names, config)
    if not ports:
        output.error("No valid ports found in specified lists")
        sys.exit(1)
    output.info(f"Scanning {len(ports)} ports from lists: {', '.join(list_names)}")
    output.info(f"Using {args.threads} threads for parallel scanning")
    output.separator()
    open_ports: List[int] = []
    closed_ports: List[int] = []
    service_results: Dict[int, Dict[str, Any]] = {}

    # Use NetworkUtils for parallel scanning
    port_list = list(ports.keys())
    network_utils.timeout = args.timeout

    # Use the built-in scan_ports method from NetworkUtils which uses ThreadPoolExecutor
    results = network_utils.scan_ports(args.host, port_list, max_workers=args.threads)

    # Process results
    for port, is_open in results.items():
        if is_open:
            open_ports.append(port)
            output.info(f"Port {port:5} ({ports[port]:25}): OPEN")
        else:
            closed_ports.append(port)
            if args.show_closed:
                output.info(f"Port {port:5} ({ports[port]:25}): CLOSED")
    # Service detection on open ports
    if detect_services and open_ports:
        output.info(f"Detecting services on {len(open_ports)} open ports...")

        for port in open_ports:
            service_info = comprehensive_service_detection(
                args.host, port, args.timeout
            )
            service_results[port] = service_info

    # Display results
    output.blank()
    output.separator()
    if output.rich_console and HAS_RICH:
        print_scan_results_rich(
            open_ports,
            closed_ports,
            ports,
            service_results,
            config,
            detect_services,
        )
    else:
        for port in sorted(open_ports):
            expected_service = ports[port]
            if detect_services and port in service_results:
                detected = service_results[port]
                confidence_emoji = {
                    "high": "🎯",
                    "medium": "🔍",
                    "low": "❓",
                }.get(detected["confidence"], "❓")
                method_emoji = "🚀" if detected["method"] == "enhanced" else "🔧"
                service_display = detected["service"]
                if detected["version"]:
                    service_display += f" ({detected['version'][:30]})"
                output.info(
                    f"Port {port:5} | Expected: {expected_service:20} | "
                    f"Detected: {confidence_emoji}{method_emoji} {service_display}"
                )
            else:
                output.info(f"Port {port:5} | {expected_service:25} | OPEN")
        output.separator()
        output.info(f"Summary: {len(open_ports)} open out of {len(ports)} scanned")


def print_scan_results_rich(
    open_ports: List[int],
    closed_ports: List[int],
    all_ports: Dict[int, str],
    service_results: Dict[int, Dict[str, Any]],
    config: Dict[str, Any],
    detect_services: bool,
) -> None:
    """Print scan results using rich tables and panels"""
    if console is None:
        return

    # Summary Table
    summary_table = Table(title="Port Scan Results", box=box.SIMPLE)
    summary_table.add_column("Port", style="bold cyan", justify="right")
    summary_table.add_column("Expected Service", style="magenta")
    summary_table.add_column("Status", style="green")
    summary_table.add_column("Detected Service", style="yellow")

    for port in sorted(all_ports.keys()):
        expected_service = all_ports[port]
        status = "OPEN" if port in open_ports else "CLOSED"
        status_color = "green" if status == "OPEN" else "red"
        detected = service_results.get(port) if detect_services else None
        detected_service = ""
        if detect_services and detected:
            confidence_emoji = {"high": "🎯", "medium": "🔍", "low": "❓"}.get(
                detected["confidence"], "❓"
            )
            method_emoji = "🚀" if detected["method"] == "enhanced" else "🔧"
            detected_service = f"{confidence_emoji}{method_emoji} {detected['service']}"
            if detected["version"]:
                detected_service += f" ({detected['version'][:30]})"
        summary_table.add_row(
            str(port),
            expected_service,
            f"[{status_color}]{status}[/{status_color}]",
            detected_service,
        )

    console.print(summary_table)

    # Category breakdown
    category_table = Table(title="Results by Category", box=box.SIMPLE)
    category_table.add_column("Category", style="bold blue")
    category_table.add_column("Open", style="green")
    category_table.add_column("Total", style="white")
    category_table.add_column("Open Ports", style="cyan")
    for list_name, details in config["port_lists"].items():
        category_open = []
        category_total = 0
        for port_str, service in details["ports"].items():
            port = int(port_str)
            category_total += 1
            if port in open_ports:
                category_open.append(port)
        category_table.add_row(
            list_name,
            str(len(category_open)),
            str(category_total),
            ", ".join(map(str, sorted(category_open))) if category_open else "-",
        )
    console.print(category_table)

    # Summary panel
    summary_text = f"[bold green]Open:[/bold green] {len(open_ports)}  "
    summary_text += f"[bold red]Closed:[/bold red] {len(closed_ports)}  "
    summary_text += f"[bold white]Total:[/bold white] {len(all_ports)}"
    console.print(Panel(summary_text, title="Scan Summary", style="bold magenta"))


def scan_all_configured_ports(
    host: str,
    timeout: float = 3,
    show_closed: bool = False,
    detect_services: bool = True,
    threads: int = 50,
) -> List[int]:
    """Scan all ports from all configured port lists with optional service detection using parallel threads"""
    config = load_port_config()
    all_ports: Dict[int, str] = {}

    # Combine all ports from all lists
    for list_name, details in config["port_lists"].items():
        ports = details["ports"]
        for port_str, service in ports.items():
            port = int(port_str)
            if port not in all_ports:
                all_ports[port] = service

    if not all_ports:
        output.error("No ports configured")
        return []

    output.info(f"Scanning ALL configured ports ({len(all_ports)} total) on {host}")
    output.info(f"Using {threads} threads for parallel scanning")
    if detect_services:
        deps, missing = check_optional_dependencies()
        enhanced = network_utils.has_requests
        method = "enhanced" if enhanced else "basic"
        output.info(f"Service detection enabled ({method} mode)")
        if missing and not enhanced:
            output.info(f"Install {', '.join(missing)} for enhanced detection")
    output.info(f"Port lists included: {', '.join(config['port_lists'].keys())}")
    output.separator(char="=", length=90)

    open_ports: List[int] = []
    closed_ports: List[int] = []
    service_results: Dict[int, Dict[str, Any]] = {}

    # Use NetworkUtils for parallel scanning
    port_list = list(all_ports.keys())
    network_utils.timeout = timeout

    # Use the built-in scan_ports method from NetworkUtils which uses ThreadPoolExecutor
    results = network_utils.scan_ports(host, port_list, max_workers=threads)

    # Process results
    for port, is_open in results.items():
        if is_open:
            open_ports.append(port)
        else:
            closed_ports.append(port)
            if show_closed:
                output.info(f"Port {port:5} ({all_ports[port]:25}): CLOSED")

    # Second pass: Service detection on open ports
    if detect_services and open_ports:
        output.info(f"Detecting services on {len(open_ports)} open ports...")

        # Use ThreadPoolExecutor for parallel service detection
        from concurrent.futures import ThreadPoolExecutor

        # Using ThreadPoolExecutor for parallel service detection
        service_results = {}
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit all service detection tasks
            future_to_port = {
                executor.submit(
                    comprehensive_service_detection, host, port, timeout
                ): port
                for port in open_ports
            }

            # Process results as they complete
            for future in future_to_port:
                port = future_to_port[future]
                try:
                    service_results[port] = future.result()
                except Exception as e:
                    output.debug(f"Error detecting service on port {port}: {e}")
                    service_results[port] = create_empty_service_result()

    # Display results
    output.blank()
    output.separator(char="=", length=90)
    if HAS_RICH and console:
        print_scan_results_rich(
            open_ports,
            closed_ports,
            all_ports,
            service_results,
            config,
            detect_services,
        )
    else:
        if detect_services:
            output.info("OPEN PORTS WITH SERVICE DETECTION:")
        else:
            output.info("OPEN PORTS:")
        output.separator(char="=", length=90)
        for port in sorted(open_ports):
            expected_service = all_ports[port]
            if detect_services and port in service_results:
                detected = service_results[port]
                confidence_emoji = {"high": "🎯", "medium": "🔍", "low": "❓"}.get(
                    detected["confidence"], "❓"
                )
                method_emoji = "🚀" if detected["method"] == "enhanced" else "🔧"
                service_display = detected["service"]
                if detected["version"]:
                    service_display += f" ({detected['version'][:30]})"
                output.info(
                    f"Port {port:5} | Expected: {expected_service:20} | "
                    f"Detected: {confidence_emoji}{method_emoji} {service_display}"
                )
                if "details" in detected and detected["details"]:
                    details = detected["details"]
                    if details.get("title"):
                        output.info(f"        └─ Title: {details['title']}")
                    if details.get("server"):
                        output.info(f"        └─ Server: {details['server']}")
                    if details.get("redirect"):
                        output.info(f"        └─ Redirects to: {details['redirect']}")
            else:
                output.info(f"Port {port:5} | {expected_service:25} | OPEN")
        output.separator(char="=", length=90)
        output.info(
            f"Summary: {len(open_ports)} open, {len(closed_ports)} closed out of {len(all_ports)} total"
        )
        if open_ports:
            output.info(f"Open ports: {', '.join(map(str, sorted(open_ports)))}")
        # Show breakdown by category
        output.info("Results by category:")
        for list_name, details in config["port_lists"].items():
            category_open = []
            category_total = 0
            for port_str, service in details["ports"].items():
                port = int(port_str)
                category_total += 1
                if port in open_ports:
                    category_open.append(port)
            if category_open:
                output.info(
                    f"  {list_name:12}: {len(category_open)}/{category_total} open - {', '.join(map(str, sorted(category_open)))}"
                )
            else:
                output.info(f"  {list_name:12}: 0/{category_total} open")

    return open_ports


def scan_port_range(
    host: str, start_port: int, end_port: int, timeout: float = 3, threads: int = 50
) -> List[int]:
    """Scan a range of ports using parallel threads"""
    ports_to_scan = list(range(start_port, end_port + 1))

    output.info(
        f"Scanning ports {start_port}-{end_port} on {host} ({len(ports_to_scan)} ports)"
    )
    output.info(f"Using {threads} threads for parallel scanning")
    output.separator()

    open_ports = []

    # Use NetworkUtils for parallel scanning
    network_utils.timeout = timeout

    # Use the built-in scan_ports method from NetworkUtils which uses ThreadPoolExecutor
    results = network_utils.scan_ports(host, ports_to_scan, max_workers=threads)

    # Process results
    for port, is_open in results.items():
        if is_open:
            open_ports.append(port)
            output.info(f"Port {port:5}: OPEN")

    output.separator()
    output.info(f"Summary: {len(open_ports)} open out of {len(ports_to_scan)} scanned")
    if open_ports:
        output.info(f"Open ports: {', '.join(map(str, sorted(open_ports)))}")

    return open_ports


def handle_default_scan(args: argparse.Namespace, detect_services: bool) -> None:
    scan_all_configured_ports(
        args.host, args.timeout, args.show_closed, detect_services, args.threads
    )


def handle_range_scan(args: argparse.Namespace) -> None:
    start_port, end_port = args.range
    if start_port > end_port or start_port < 1 or end_port > 65535:
        output.error("Invalid port range. Ports must be 1-65535 and start <= end")
        sys.exit(1)
    scan_port_range(args.host, start_port, end_port, args.timeout, args.threads)


def handle_port_scan(args: argparse.Namespace, detect_services: bool) -> None:
    output.info(f"Checking port {args.port} on {args.host}...")
    is_open = check_port(args.host, args.port, args.timeout)
    status = "OPEN" if is_open else "CLOSED"
    output.info(f"Port {args.port}: {status}")
    if is_open and detect_services:
        output.info("Detecting service...")
        service_info = comprehensive_service_detection(
            args.host, args.port, args.timeout
        )
        output.info(
            f"Service: {service_info['service']} ({service_info['method']} mode)"
        )
        if service_info["version"]:
            output.info(f"Version: {service_info['version']}")


def create_argument_parser() -> ArgumentParser:
    """Create and configure argument parser"""
    parser = ArgumentParser(
        tool_name=TOOL_NAME,
        description="Port scanner and service checker with TOML configuration",
        epilog="""
Examples:
  scan-ports localhost        Scan localhost with default port list
  scan-ports 192.168.1.1      Scan a specific IP address
  scan-ports --list web       Scan ports from the 'web' list
  scan-ports -p 8080          Check a specific port
  scan-ports --show-lists     Show available port lists
  scan-ports --check-deps     Check optional dependency status

By default, scans ALL ports defined in the TOML configuration file with service detection.
        """,
        version=__version__,
    )

    # Add common arguments
    parser.add_common_arguments()

    # Add tool-specific arguments
    parser.add_positional_argument(
        "host", "Host to scan (default: localhost)", nargs="?", default="localhost"
    )

    parser.add_option("port", "Check specific port", short_name="p", type=int)

    parser.parser.add_argument(
        "-r",
        "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Scan port range (e.g., -r 1000 2000)",
    )

    parser.add_option(
        "list",
        "Scan ports from specific lists (comma-separated, e.g., 'web,database')",
        short_name="l",
    )

    parser.add_flag("show-lists", "Show available port lists and exit")

    parser.add_flag("show-closed", "Show closed ports in output")

    parser.add_flag(
        "no-service-detection", "Disable service detection (faster scanning)"
    )

    # Add a --show-config flag to match other tools
    parser.add_flag("show-config", "Show configuration debug info")

    parser.add_option(
        "timeout",
        "Connection timeout in seconds (default: 3)",
        short_name="t",
        default=3,
        type=float,
    )

    parser.add_flag("fast", "Fast scan with shorter timeout")

    parser.add_option(
        "threads", "Number of concurrent threads (default: 50)", default=50, type=int
    )

    # Add standard logging options
    parser.parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level",
    )
    parser.parser.add_argument(
        "--log-file", action="store_true", help="Log output to a file"
    )
    parser.parser.add_argument("--log-file-path", help="Specify custom log file path")

    return parser


def main() -> None:
    # Create the argument parser and parse arguments
    parser = create_argument_parser()
    args = parser.parser.parse_args()

    # Initialize globals
    global output, error_handler, config_loader, network_utils

    # Configure output based on arguments
    output = setup_tool_output(
        tool_name=TOOL_NAME,
        log_level=args.log_level if hasattr(args, "log_level") else "INFO",
        log_to_file=args.log_file if hasattr(args, "log_file") else False,
        log_file_path=args.log_file_path if hasattr(args, "log_file_path") else "",
        use_rich=not args.no_color if hasattr(args, "no_color") else True,
    )

    # Initialize other shared utilities with proper output
    error_handler = ErrorHandler(output)
    config_loader = ConfigLoader(TOOL_NAME, output.logger)
    network_utils = create_network_utils(timeout=args.timeout, logger=output.logger)

    # Display tool banner
    output.banner(
        TOOL_NAME,
        __version__,
        {
            "Description": "Scan local or remote hosts for open ports and detect services"
        },
    )

    # Apply any command-line overrides
    if args.fast:
        args.timeout = 1

    # Re-initialize network_utils with the potentially adjusted timeout
    network_utils = create_network_utils(timeout=args.timeout, logger=output.logger)

    detect_services = not args.no_service_detection

    output.info(f"Target: {args.host}")
    output.info(f"Timeout: {args.timeout}s")
    output.info(f"Threads: {args.threads}")
    output.info(f"Service Detection: {'Enabled' if detect_services else 'Disabled'}")
    if detect_services:
        print_dependency_status(verbose=False)
    output.blank()

    # Handle special commands first
    if args.check_deps:
        print_dependency_status(verbose=True)
        return

    if args.show_config:
        output.info(
            f"TOML Support: {'Available' if config_loader.has_toml else 'Missing'}"
        )
        output.info(f"Service Detection Available: {HAS_REQUESTS and HAS_URLLIB3}")
        # Show the config that will be used
        config = load_port_config()
        output.info(f"Number of Port Lists: {len(config.get('port_lists', {}))}")
        return

    if args.show_lists:
        list_available_port_lists()
        return

    try:
        if args.port:
            handle_port_scan(args, detect_services)
        elif args.range:
            handle_range_scan(args)
        elif args.list:
            handle_list_scan(args, detect_services)
        else:
            handle_default_scan(args, detect_services)
    except KeyboardInterrupt:
        output.warning("Scan interrupted by user")
        sys.exit(0)
    except Exception as e:
        output.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
