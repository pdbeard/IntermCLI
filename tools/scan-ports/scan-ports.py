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

import argparse
import re
import socket
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# TOML support with fallback
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # fallback for older Python
    except ImportError:
        tomllib = None

# Optional dependencies with fallbacks
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import urllib3

    HAS_URLLIB3 = True
except ImportError:
    HAS_URLLIB3 = False

# Add rich support
try:
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# SSL support detection
try:
    import importlib.util

    HAS_SSL = importlib.util.find_spec("ssl") is not None
except Exception:
    HAS_SSL = False


def check_optional_dependencies():
    """Check which optional dependencies are available"""
    deps = {
        "requests": HAS_REQUESTS,
        "urllib3": HAS_URLLIB3,
        "ssl": HAS_SSL,
        "tomllib": tomllib is not None,
    }

    missing = [name for name, available in deps.items() if not available]

    return deps, missing


def print_dependency_status(verbose=False):
    """Print status of optional dependencies"""
    deps, missing = check_optional_dependencies()

    if verbose:
        print("📦 Optional Dependencies Status:")
        for name, available in deps.items():
            status = "✅ Available" if available else "❌ Missing"
            print(f"  {name:10}: {status}")

        if missing:
            if "tomllib" in missing:
                print("\n💡 For TOML support on Python < 3.11: pip3 install tomli")
            other_missing = [m for m in missing if m != "tomllib"]
            if other_missing:
                print(
                    f"💡 To enable enhanced service detection: pip3 install {' '.join(other_missing)}"
                )
        print()


def load_port_config():
    """Load port configuration from TOML file"""
    script_dir = Path(__file__).parent
    source_config_file = script_dir / "config" / "ports.toml"
    user_config_dir = Path.home() / ".config" / "intermcli"
    user_config_file = user_config_dir / "scan-ports.toml"
    legacy_user_config_file = user_config_dir / "config.toml"

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

    if not tomllib:
        print("⚠️  TOML support not available")
        print("💡 Install tomli for Python < 3.11: pip3 install tomli")
        print("💡 Using default port list")
        return default_config

    try:
        config_loaded = None
        config_data = None
        if user_config_file.exists():
            with open(user_config_file, "rb") as f:
                config_data = tomllib.load(f)
            config_loaded = str(user_config_file)
        elif legacy_user_config_file.exists():
            with open(legacy_user_config_file, "rb") as f:
                config_data = tomllib.load(f)
            config_loaded = str(legacy_user_config_file)
        elif source_config_file.exists():
            with open(source_config_file, "rb") as f:
                config_data = tomllib.load(f)
            config_loaded = str(source_config_file)
        else:
            print("⚠️  Config file not found in any location.")
            print("💡 Using default port list")
            return default_config

        if config_loaded:
            print(f"ℹ️  Loaded port config: {config_loaded}")
        return config_data if config_data else default_config
    except Exception as e:
        print(f"⚠️  Error loading TOML config: {e}")
        print("💡 Using default port list")
        return default_config


def list_available_port_lists():
    """Display all available port lists from configuration"""
    config = load_port_config()

    print("📋 Available Port Lists:")
    print("=" * 60)

    for list_name, details in config["port_lists"].items():
        description = details.get("description", "No description")
        ports = details.get("ports", {})

        print(f"\n🏷️  {list_name.upper()}")
        print(f"   Description: {description}")
        print(f"   Ports: {len(ports)} defined")

        # Show first few ports as preview
        port_preview = list(ports.items())[:5]
        for port, service in port_preview:
            print(f"   • {port}: {service}")

        if len(ports) > 5:
            print(f"   ... and {len(ports) - 5} more")

    print("\n" + "=" * 60)
    print("💡 Usage: scan-ports -l <list_name> or scan-ports -l <list1>,<list2>")
    print("💡 Example: scan-ports -l web,database")


def get_ports_from_lists(list_names, config):
    """Get ports from specified lists, or all if 'all' is specified"""
    ports = {}
    available_lists = list(config["port_lists"].keys())

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
            print(f"⚠️  Port list '{list_name}' not found")
            print(f"Available lists: {', '.join(available_lists)}")

    return ports


def check_port(host, port, timeout=3):
    """Check if a specific port is open"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False


def detect_service_banner_basic(host, port, timeout=3):
    """Basic service banner detection using only standard library"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))

            # Send common probes
            probes = [
                b"",  # Just connect
                b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n",  # HTTP probe
                b"\r\n",  # Generic newline
                b"HELP\r\n",  # Generic help command
            ]

            for probe in probes:
                try:
                    if probe:
                        sock.send(probe)

                    # Try to receive response
                    sock.settimeout(2)
                    response = sock.recv(1024).decode("utf-8", errors="ignore")

                    if response.strip():
                        return response[:200]  # Limit response length

                except (socket.timeout, socket.error):
                    continue

        return None
    except Exception:
        return None


def detect_http_service_basic(host, port, timeout=5):
    """Basic HTTP detection using urllib (standard library)"""
    try:
        import urllib.error
        import urllib.request

        protocols = ["http"]
        if port in [443, 8443] and HAS_SSL:
            protocols = ["https", "http"]

        for protocol in protocols:
            try:
                url = f"{protocol}://{host}:{port}"

                # Create request with custom headers
                req = urllib.request.Request(
                    url, headers={"User-Agent": "port-check/1.0"}
                )

                # Create SSL context that ignores cert errors
                if protocol == "https" and HAS_SSL:
                    import ssl

                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
                else:
                    response = urllib.request.urlopen(req, timeout=timeout)

                content = response.read().decode("utf-8", errors="ignore")
                headers = dict(response.headers)

                service_info = {
                    "protocol": protocol,
                    "status_code": response.status,
                    "server": headers.get("Server", "Unknown"),
                    "title": None,
                    "framework": None,
                }

                # Try to extract page title
                title_match = re.search(
                    r"<title[^>]*>([^<]+)</title>", content, re.IGNORECASE
                )
                if title_match:
                    service_info["title"] = title_match.group(1).strip()[:50]

                # Basic framework detection
                content_lower = (content + str(headers)).lower()
                frameworks = {
                    "Django": ["django", "csrftoken"],
                    "Flask": ["flask", "werkzeug"],
                    "Express.js": ["express"],
                    "Apache": ["apache"],
                    "Nginx": ["nginx"],
                    "React": ["react"],
                    "Jenkins": ["jenkins"],
                    "Grafana": ["grafana"],
                }

                for framework, indicators in frameworks.items():
                    if any(indicator in content_lower for indicator in indicators):
                        service_info["framework"] = framework
                        break

                return service_info

            except (urllib.error.URLError, socket.timeout):
                continue
            except Exception:
                continue

    except ImportError:
        pass

    return None


def detect_http_service_enhanced(host, port, timeout=5):
    """Enhanced HTTP detection using requests library"""
    if not HAS_REQUESTS:
        return detect_http_service_basic(host, port, timeout)

    protocols = ["http", "https"] if port in [443, 8443] else ["http"]

    for protocol in protocols:
        try:
            url = f"{protocol}://{host}:{port}"

            # Disable SSL warnings if urllib3 is available
            if HAS_URLLIB3:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            response = requests.get(
                url,
                timeout=timeout,
                verify=False,  # Allow self-signed certs
                allow_redirects=False,
                headers={"User-Agent": "port-check/1.0"},
            )

            service_info = {
                "protocol": protocol,
                "status_code": response.status_code,
                "server": response.headers.get("Server", "Unknown"),
                "title": None,
                "framework": None,
                "redirect": response.headers.get("Location"),
            }

            # Try to extract page title
            if "text/html" in response.headers.get("Content-Type", ""):
                title_match = re.search(
                    r"<title[^>]*>([^<]+)</title>", response.text, re.IGNORECASE
                )
                if title_match:
                    service_info["title"] = title_match.group(1).strip()[:50]

            # Enhanced framework detection
            framework_indicators = {
                "Django": ["csrftoken", "django"],
                "Flask": ["flask", "werkzeug"],
                "Express.js": ["express", "x-powered-by: express"],
                "Apache": ["apache"],
                "Nginx": ["nginx"],
                "React": ["react", "__REACT_DEVTOOLS"],
                "Vue.js": ["vue", "__VUE__"],
                "Jenkins": ["jenkins", "x-jenkins"],
                "Grafana": ["grafana"],
                "Prometheus": ["prometheus"],
                "GitLab": ["gitlab"],
                "Jupyter": ["jupyter", "notebook"],
                "Portainer": ["portainer"],
                "SonarQube": ["sonarqube"],
            }

            response_text = (response.text + str(response.headers)).lower()
            for framework, indicators in framework_indicators.items():
                if any(indicator in response_text for indicator in indicators):
                    service_info["framework"] = framework
                    break

            return service_info

        except Exception:
            continue

    return None


def detect_database_service_enhanced(host, port, timeout=3):
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

    if port in database_signatures:
        # Try specific database probes
        if port == 6379:  # Redis
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    sock.connect((host, port))
                    sock.send(b"INFO\r\n")
                    response = sock.recv(1024).decode("utf-8", errors="ignore")
                    if "redis_version" in response.lower():
                        version_match = re.search(r"redis_version:([^\r\n]+)", response)
                        if version_match:
                            return f"Redis {version_match.group(1)}"
                        return "Redis"
            except Exception:
                pass

        elif port == 9200:  # Elasticsearch
            # Try with requests first, fallback to basic HTTP
            es_info = None
            if HAS_REQUESTS:
                try:
                    response = requests.get(f"http://{host}:{port}", timeout=timeout)
                    if response.status_code == 200:
                        data = response.json()
                        if "version" in data:
                            return f"Elasticsearch {data['version']['number']}"
                        return "Elasticsearch"
                except Exception:
                    pass

            # Fallback to basic detection
            if not es_info:
                try:
                    import urllib.request

                    response = urllib.request.urlopen(
                        f"http://{host}:{port}", timeout=timeout
                    )
                    content = response.read().decode("utf-8")
                    if "elasticsearch" in content.lower():
                        return "Elasticsearch"
                except Exception:
                    pass

    return database_signatures.get(port)


def detect_ssh_service(host, port, timeout=3):
    """Detect SSH service version"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))

            # SSH servers send banner immediately
            banner = sock.recv(1024).decode("utf-8", errors="ignore")
            if banner.startswith("SSH"):
                return banner.strip()

    except Exception:
        pass

    return "SSH"


def comprehensive_service_detection(host, port, timeout=3, enhanced=None):
    """Comprehensive service detection with fallback options"""
    if enhanced is None:
        enhanced = HAS_REQUESTS  # Use enhanced features if available

    service_info = {
        "service": "Unknown",
        "version": None,
        "details": {},
        "confidence": "low",
        "method": "basic" if not enhanced else "enhanced",
    }

    # Try HTTP detection first for web services
    if port in [80, 443, 8080, 8443, 3000, 4000, 5000, 8000, 9000]:
        if enhanced:
            http_info = detect_http_service_enhanced(host, port, timeout)
        else:
            http_info = detect_http_service_basic(host, port, timeout)

        if http_info:
            service_info["service"] = (
                http_info.get("framework") or f"HTTP ({http_info['protocol'].upper()})"
            )
            service_info["details"] = http_info
            service_info["confidence"] = "high"
            return service_info

    # Try SSH detection
    if port == 22:
        ssh_banner = detect_ssh_service(host, port, timeout)
        if ssh_banner:
            service_info["service"] = "SSH"
            service_info["version"] = ssh_banner
            service_info["confidence"] = "high"
            return service_info

    # Try database detection
    db_service = detect_database_service_enhanced(host, port, timeout)
    if db_service:
        service_info["service"] = db_service
        service_info["confidence"] = "medium"
        return service_info

    # Try generic banner grabbing
    banner = detect_service_banner_basic(host, port, timeout)
    if banner:
        service_info["version"] = banner
        service_info["confidence"] = "medium"

        # Try to identify service from banner
        banner_lower = banner.lower()
        if "ssh" in banner_lower:
            service_info["service"] = "SSH"
        elif "http" in banner_lower or "html" in banner_lower:
            service_info["service"] = "HTTP"
        elif "ftp" in banner_lower:
            service_info["service"] = "FTP"
        elif "smtp" in banner_lower:
            service_info["service"] = "SMTP"
        elif "mysql" in banner_lower:
            service_info["service"] = "MySQL"
        elif "postgres" in banner_lower:
            service_info["service"] = "PostgreSQL"

    return service_info


def print_scan_results_rich(
    open_ports, closed_ports, all_ports, service_results, config, detect_services
):
    """Print scan results using rich tables and panels"""
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


def scan_all_configured_ports(host, timeout=3, show_closed=False, detect_services=True):
    """Scan all ports from all configured port lists with optional service detection"""
    config = load_port_config()
    all_ports = {}

    # Combine all ports from all lists
    for list_name, details in config["port_lists"].items():
        ports = details["ports"]
        for port_str, service in ports.items():
            port = int(port_str)
            if port not in all_ports:
                all_ports[port] = service

    if not all_ports:
        print("❌ No ports configured")
        return []

    print(f"🔍 Scanning ALL configured ports ({len(all_ports)} total) on {host}")
    if detect_services:
        deps, missing = check_optional_dependencies()
        enhanced = HAS_REQUESTS
        method = "enhanced" if enhanced else "basic"
        print(f"🔬 Service detection enabled ({method} mode)")
        if missing and not enhanced:
            print(f"💡 Install {', '.join(missing)} for enhanced detection")
    print("📋 Port lists included:", ", ".join(config["port_lists"].keys()))
    print("=" * 90)

    open_ports = []
    closed_ports = []
    service_results = {}

    # First pass: Check which ports are open
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {
            executor.submit(check_port, host, port, timeout): (port, service)
            for port, service in all_ports.items()
        }

        for future in futures:
            port, expected_service = futures[future]
            is_open = future.result()
            if is_open:
                open_ports.append(port)
            else:
                closed_ports.append(port)
                if show_closed:
                    print(f"Port {port:5} ({expected_service:25}): ❌ CLOSED")

    # Second pass: Service detection on open ports
    if detect_services and open_ports:
        print(f"\n🔬 Detecting services on {len(open_ports)} open ports...")

        with ThreadPoolExecutor(
            max_workers=10
        ) as executor:  # Fewer threads for service detection
            futures = {
                executor.submit(
                    comprehensive_service_detection, host, port, timeout
                ): port
                for port in open_ports
            }

            for future in futures:
                port = futures[future]
                service_info = future.result()
                service_results[port] = service_info

    # Display results
    print("\n" + "=" * 90)
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
            print("📊 OPEN PORTS WITH SERVICE DETECTION:")
        else:
            print("📊 OPEN PORTS:")
        print("=" * 90)
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
                print(
                    f"Port {port:5} | Expected: {expected_service:20} | "
                    f"Detected: {confidence_emoji}{method_emoji} {service_display}"
                )
                if "details" in detected and detected["details"]:
                    details = detected["details"]
                    if details.get("title"):
                        print(f"        └─ Title: {details['title']}")
                    if details.get("server"):
                        print(f"        └─ Server: {details['server']}")
                    if details.get("redirect"):
                        print(f"        └─ Redirects to: {details['redirect']}")
            else:
                print(f"Port {port:5} | {expected_service:25} | ✅ OPEN")
        print("=" * 90)
        print(
            f"📊 Summary: {len(open_ports)} open, {len(closed_ports)} closed out of {len(all_ports)} total"
        )
        if open_ports:
            print(f"🔓 Open ports: {', '.join(map(str, sorted(open_ports)))}")
        # Show breakdown by category
        print("\n📂 Results by category:")
        for list_name, details in config["port_lists"].items():
            category_open = []
            category_total = 0
            for port_str, service in details["ports"].items():
                port = int(port_str)
                category_total += 1
                if port in open_ports:
                    category_open.append(port)
            if category_open:
                print(
                    f"  {list_name:12}: {len(category_open)}/{category_total} open - {', '.join(map(str, sorted(category_open)))}"
                )
            else:
                print(f"  {list_name:12}: 0/{category_total} open")

    return open_ports


def scan_port_range(host, start_port, end_port, timeout=3, threads=50):
    """Scan a range of ports"""
    ports_to_scan = list(range(start_port, end_port + 1))

    print(
        f"🔍 Scanning ports {start_port}-{end_port} on {host} ({len(ports_to_scan)} ports)"
    )
    print("=" * 60)

    open_ports = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(check_port, host, port, timeout): port
            for port in ports_to_scan
        }

        for future in futures:
            port = futures[future]
            is_open = future.result()
            if is_open:
                open_ports.append(port)
                print(f"Port {port:5}: ✅ OPEN")

    print("=" * 60)
    print(f"📊 Summary: {len(open_ports)} open out of {len(ports_to_scan)} scanned")
    if open_ports:
        print(f"🔓 Open ports: {', '.join(map(str, sorted(open_ports)))}")

    return open_ports


__version__ = "0.1.0"


def main():
    parser = argparse.ArgumentParser(
        description="Port scanner and service checker with TOML configuration",
        epilog="By default, scans ALL ports defined in the TOML configuration file with service detection.",
    )
    parser.add_argument(
        "host", nargs="?", default="localhost", help="Host to scan (default: localhost)"
    )
    parser.add_argument("-p", "--port", type=int, help="Check specific port")
    parser.add_argument(
        "-r",
        "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Scan port range (e.g., -r 1000 2000)",
    )
    parser.add_argument(
        "-l",
        "--list",
        type=str,
        help="Scan ports from specific lists (comma-separated, e.g., 'web,database')",
    )
    parser.add_argument(
        "--show-lists", action="store_true", help="Show available port lists and exit"
    )
    parser.add_argument(
        "--show-closed", action="store_true", help="Show closed ports in output"
    )
    parser.add_argument(
        "--no-service-detection",
        action="store_true",
        help="Disable service detection (faster scanning)",
    )
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check optional dependency status and exit",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=3,
        help="Connection timeout in seconds (default: 3)",
    )
    parser.add_argument(
        "--fast", action="store_true", help="Fast scan with shorter timeout"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=50,
        help="Number of concurrent threads (default: 50)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"scan-ports {__version__}",
        help="Show version and exit",
    )

    args = parser.parse_args()

    if args.check_deps:
        print_dependency_status(verbose=True)
        return

    if args.show_lists:
        list_available_port_lists()
        return

    if args.fast:
        args.timeout = 1

    detect_services = not args.no_service_detection

    print(f"🎯 Target: {args.host}")
    print(f"⏱️  Timeout: {args.timeout}s")
    print(f"🧵 Threads: {args.threads}")
    print(f"🔬 Service Detection: {'Enabled' if detect_services else 'Disabled'}")
    if detect_services:
        print_dependency_status(verbose=False)
    print()

    try:
        if args.port:
            # Check single port with service detection
            print(f"🔍 Checking port {args.port} on {args.host}...")
            is_open = check_port(args.host, args.port, args.timeout)
            status = "✅ OPEN" if is_open else "❌ CLOSED"
            print(f"Port {args.port}: {status}")

            if is_open and detect_services:
                print("🔬 Detecting service...")
                service_info = comprehensive_service_detection(
                    args.host, args.port, args.timeout
                )
                print(
                    f"Service: {service_info['service']} ({service_info['method']} mode)"
                )
                if service_info["version"]:
                    print(f"Version: {service_info['version']}")

        elif args.range:
            # Scan port range (no service detection for ranges)
            start_port, end_port = args.range
            if start_port > end_port or start_port < 1 or end_port > 65535:
                print("❌ Invalid port range. Ports must be 1-65535 and start <= end")
                sys.exit(1)

            scan_port_range(args.host, start_port, end_port, args.timeout, args.threads)

        elif args.list:
            # Scan specific port lists
            config = load_port_config()
            list_names = [name.strip() for name in args.list.split(",")]
            ports = get_ports_from_lists(list_names, config)

            if not ports:
                print("❌ No valid ports found in specified lists")
                sys.exit(1)

            print(f"🔍 Scanning {len(ports)} ports from lists: {', '.join(list_names)}")
            print("=" * 60)

            open_ports = []
            closed_ports = [port for port in ports if port not in open_ports]
            service_results = {}

            # Check ports
            with ThreadPoolExecutor(max_workers=args.threads) as executor:
                futures = {
                    executor.submit(check_port, args.host, port, args.timeout): (
                        port,
                        service,
                    )
                    for port, service in ports.items()
                }

                for future in futures:
                    port, expected_service = futures[future]
                    is_open = future.result()
                    if is_open:
                        open_ports.append(port)
                    elif args.show_closed:
                        print(f"Port {port:5} ({expected_service:25}): ❌ CLOSED")

            # Service detection on open ports
            if detect_services and open_ports:
                print(f"\n🔬 Detecting services on {len(open_ports)} open ports...")

                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {
                        executor.submit(
                            comprehensive_service_detection,
                            args.host,
                            port,
                            args.timeout,
                        ): port
                        for port in open_ports
                    }

                    for future in futures:
                        port = futures[future]
                        service_info = future.result()
                        service_results[port] = service_info

            # Display results
            print("\n" + "=" * 60)
            if HAS_RICH and console:
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

                        method_emoji = (
                            "🚀" if detected["method"] == "enhanced" else "🔧"
                        )
                        service_display = detected["service"]
                        if detected["version"]:
                            service_display += f" ({detected['version'][:30]})"

                        print(
                            f"Port {port:5} | Expected: {expected_service:20} | "
                            f"Detected: {confidence_emoji}{method_emoji} {service_display}"
                        )
                    else:
                        print(f"Port {port:5} | {expected_service:25} | ✅ OPEN")

                print("=" * 60)
                print(f"📊 Summary: {len(open_ports)} open out of {len(ports)} scanned")

        else:
            # DEFAULT: Scan ALL configured ports with optional service detection
            scan_all_configured_ports(
                args.host, args.timeout, args.show_closed, detect_services
            )

    except KeyboardInterrupt:
        print("\n⏹️  Scan interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
