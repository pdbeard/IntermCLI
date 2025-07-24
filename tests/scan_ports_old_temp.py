import importlib.util
import os
import sys
from unittest import mock

import pytest


def import_scan_ports():
    TOOL_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../tools/scan-ports/scan-ports.py")
    )
    spec = importlib.util.spec_from_file_location("scan_ports", TOOL_PATH)
    scan_ports = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan_ports)
    return scan_ports


def test_missing_rich(monkeypatch):
    sys_modules_backup = sys.modules.copy()
    sys.modules["rich"] = None
    sys.modules["rich.console"] = None
    sys.modules["rich.table"] = None
    sys.modules["rich.panel"] = None
    sys.modules["rich.box"] = None
    scan_ports = import_scan_ports()
    assert not scan_ports.HAS_RICH
    assert scan_ports.console is None
    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_missing_requests(monkeypatch):
    sys_modules_backup = sys.modules.copy()
    sys.modules["requests"] = None
    scan_ports = import_scan_ports()
    assert not scan_ports.HAS_REQUESTS
    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_missing_toml(monkeypatch, caplog):
    sys_modules_backup = sys.modules.copy()
    sys.modules["tomllib"] = None
    sys.modules["tomli"] = None
    scan_ports = import_scan_ports()
    config = scan_ports.load_port_config()
    log = caplog.text
    assert "TOML support not available" in log or "Using default port list" in log
    assert "port_lists" in config
    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_missing_urllib3(monkeypatch):
    sys_modules_backup = sys.modules.copy()
    sys.modules["urllib3"] = None
    scan_ports = import_scan_ports()
    assert not scan_ports.HAS_URLLIB3
    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_missing_ssl(monkeypatch):
    sys_modules_backup = sys.modules.copy()
    sys.modules["ssl"] = None

    # Mock importlib.util.find_spec to return None for SSL
    original_find_spec = importlib.util.find_spec

    def mock_find_spec(name, *args, **kwargs):
        if name == "ssl":
            return None
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "find_spec", mock_find_spec)

    scan_ports = import_scan_ports()
    assert not scan_ports.HAS_SSL

    sys.modules.clear()
    sys.modules.update(sys_modules_backup)


def test_check_optional_dependencies():
    scan_ports = import_scan_ports()
    deps, missing = scan_ports.check_optional_dependencies()
    assert isinstance(deps, dict)
    assert isinstance(missing, list)


def test_print_dependency_status(capsys):
    scan_ports = import_scan_ports()
    scan_ports.print_dependency_status(verbose=True)
    out = capsys.readouterr().out
    assert "Optional Dependencies Status" in out


def test_load_port_config_default(monkeypatch, tmp_path, capsys):
    scan_ports = import_scan_ports()
    # Remove config files if present
    monkeypatch.setattr(scan_ports.Path, "home", lambda: tmp_path)
    config = scan_ports.load_port_config()
    assert "port_lists" in config


def test_list_available_port_lists(capsys):
    scan_ports = import_scan_ports()
    scan_ports.list_available_port_lists()
    out = capsys.readouterr().out
    assert "Available Port Lists" in out


def test_get_ports_from_lists_all():
    scan_ports = import_scan_ports()
    config = scan_ports.load_port_config()
    ports = scan_ports.get_ports_from_lists(["all"], config)
    assert isinstance(ports, dict)
    assert ports


def test_get_ports_from_lists_invalid(capsys):
    scan_ports = import_scan_ports()
    config = scan_ports.load_port_config()
    ports = scan_ports.get_ports_from_lists(["notalist"], config)
    out = capsys.readouterr().out
    assert "not found" in out
    assert isinstance(ports, dict)


def test_check_port_open_closed(monkeypatch):
    scan_ports = import_scan_ports()
    # Mock socket to simulate open and closed
    with mock.patch("socket.socket.connect_ex", return_value=0):
        assert scan_ports.check_port("localhost", 22, 1) is True
    with mock.patch("socket.socket.connect_ex", return_value=1):
        assert scan_ports.check_port("localhost", 22, 1) is False


def test_detect_service_banner_basic(monkeypatch):
    scan_ports = import_scan_ports()

    # Mock socket to simulate banner
    class DummySock:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def settimeout(self, t):
            pass

        def connect(self, addr):
            pass

        def send(self, data):
            pass

        def recv(self, n):
            return b"HTTP/1.1 200 OK\r\nServer: Dummy\r\n\r\n"

    monkeypatch.setattr("socket.socket", lambda *a, **kw: DummySock())
    banner = scan_ports.detect_service_banner_basic("localhost", 80, 1)
    assert "HTTP/1.1" in banner


def test_scan_all_configured_ports(monkeypatch, capsys):
    scan_ports = import_scan_ports()
    # Patch check_port to always return False (all closed)
    monkeypatch.setattr(scan_ports, "check_port", lambda *a, **kw: False)
    open_ports = scan_ports.scan_all_configured_ports(
        "localhost", timeout=0.1, show_closed=True, detect_services=False
    )
    out = capsys.readouterr().out
    assert "CLOSED" in out or "closed" in out
    assert open_ports == []


def test_scan_port_range(monkeypatch, capsys):
    scan_ports = import_scan_ports()
    # Patch check_port to return True for port 22 only
    monkeypatch.setattr(
        scan_ports, "check_port", lambda host, port, timeout: port == 22
    )
    open_ports = scan_ports.scan_port_range("localhost", 22, 23, timeout=0.1, threads=2)
    out = capsys.readouterr().out
    assert 22 in open_ports
    assert "OPEN" in out


def test_main_check_deps(monkeypatch, capsys):
    scan_ports = import_scan_ports()
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--check-deps"])
    scan_ports.main()
    out = capsys.readouterr().out
    assert "Optional Dependencies Status" in out


def test_main_show_lists(monkeypatch, capsys):
    scan_ports = import_scan_ports()
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--show-lists"])
    scan_ports.main()
    out = capsys.readouterr().out
    assert "Available Port Lists" in out


def test_main_invalid_range(monkeypatch, caplog):
    scan_ports = import_scan_ports()
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--range", "1000", "999"])
    with caplog.at_level("ERROR"):
        with pytest.raises(SystemExit):
            scan_ports.main()
    log = caplog.text
    assert "Invalid port range" in log


def test_main_no_valid_ports(monkeypatch, capsys):
    scan_ports = import_scan_ports()
    # Patch get_ports_from_lists to return empty dict
    monkeypatch.setattr(scan_ports, "get_ports_from_lists", lambda names, config: {})
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--list", "notalist"])
    with pytest.raises(SystemExit):
        scan_ports.main()
    out = capsys.readouterr().out
    assert "No valid ports found" in out


def test_main_keyboard_interrupt(monkeypatch, capsys):
    scan_ports = import_scan_ports()

    def raise_keyboard(*a, **kw):
        raise KeyboardInterrupt()

    monkeypatch.setattr(scan_ports, "scan_all_configured_ports", raise_keyboard)
    monkeypatch.setattr(sys, "argv", ["scan-ports.py"])
    with pytest.raises(SystemExit):
        scan_ports.main()
    out = capsys.readouterr().out
    assert "Scan interrupted by user" in out


def test_main_generic_exception(monkeypatch, capsys):
    scan_ports = import_scan_ports()

    def raise_exc(*a, **kw):
        raise Exception("fail")

    monkeypatch.setattr(scan_ports, "scan_all_configured_ports", raise_exc)
    monkeypatch.setattr(sys, "argv", ["scan-ports.py"])
    with pytest.raises(SystemExit):
        scan_ports.main()
    out = capsys.readouterr().out
    assert "Error: fail" in out


def test_output_class_methods(monkeypatch, caplog):
    import logging

    scan_ports = import_scan_ports()

    # Set log level to INFO to capture info messages
    with caplog.at_level(logging.INFO):
        # Test with rich disabled
        output = scan_ports.Output(use_rich=False)

        # Test different output methods
        output.info("Info message")
        output.warning("Warning message")
        output.error("Error message")
        output.separator(10)
        output.blank()
        output.print_rich("Rich object")

        # Check log output
        log = caplog.text
        assert "Info message" in log
        assert "Warning message" in log
        assert "Error message" in log
        assert "Rich object" in log


def test_detect_http_service_basic(monkeypatch):
    scan_ports = import_scan_ports()

    # Mock urllib.request
    class MockResponse:
        def __init__(self):
            self.status = 200
            self.headers = {"Server": "Apache/2.4.41"}

        def read(self):
            return (
                b"<html><head><title>Test Page</title></head><body>Hello</body></html>"
            )

    # Mock urllib.request.urlopen to return our mock response
    def mock_urlopen(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("urllib.request.urlopen", mock_urlopen)

    # Test the method
    result = scan_ports.detect_http_service_basic("localhost", 80, timeout=0.1)

    assert result is not None
    assert result["status_code"] == 200
    assert result["server"] == "Apache/2.4.41"
    assert result["title"] == "Test Page"


def test_detect_http_service_enhanced(monkeypatch):
    scan_ports = import_scan_ports()

    # Skip if requests is not available
    if not scan_ports.HAS_REQUESTS:
        pytest.skip("requests library not available")

    # Mock requests.get
    class MockRequestsResponse:
        def __init__(self):
            self.status_code = 200
            self.headers = {"Server": "nginx/1.18.0", "Content-Type": "text/html"}
            self.text = "<html><head><title>Enhanced Test</title></head><body>Enhanced response with vue.js</body></html>"

    monkeypatch.setattr("requests.get", lambda *a, **kw: MockRequestsResponse())

    # Test the method
    result = scan_ports.detect_http_service_enhanced("localhost", 80, timeout=0.1)

    assert result is not None
    assert result["status_code"] == 200
    assert result["server"] == "nginx/1.18.0"
    assert result["title"] == "Enhanced Test"
    # The framework detection depends on the implementation, don't assert exact value
    assert result["framework"] is not None


def test_detect_database_service_enhanced(monkeypatch):
    scan_ports = import_scan_ports()

    # Test Redis detection
    class MockRedisSocket:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def settimeout(self, t):
            pass

        def connect(self, addr):
            pass

        def send(self, data):
            pass

        def recv(self, n):
            return b"redis_version:6.0.9\r\nredis_mode:standalone\r\n"

    monkeypatch.setattr("socket.socket", lambda *a, **kw: MockRedisSocket())

    # Test Redis detection (port 6379)
    redis_result = scan_ports.detect_database_service_enhanced(
        "localhost", 6379, timeout=0.1
    )
    assert "Redis" in redis_result

    # Test default signature-based detection (other DB port)
    pg_result = scan_ports.detect_database_service_enhanced(
        "localhost", 5432, timeout=0.1
    )
    assert "PostgreSQL" in pg_result


def test_comprehensive_service_detection(monkeypatch):
    scan_ports = import_scan_ports()

    # Test SSH detection
    def mock_detect_ssh(*args, **kwargs):
        return "SSH-2.0-OpenSSH_8.2p1"

    # Test HTTP detection
    def mock_detect_http_enhanced(*args, **kwargs):
        return {
            "protocol": "https",
            "status_code": 200,
            "server": "nginx",
            "title": "Test Page",
            "framework": "Django",
        }

    # Test database detection
    def mock_detect_db(*args, **kwargs):
        return "PostgreSQL 13.4"

    # Test different cases
    monkeypatch.setattr(scan_ports, "detect_ssh_service", mock_detect_ssh)
    monkeypatch.setattr(
        scan_ports, "detect_http_service_enhanced", mock_detect_http_enhanced
    )
    monkeypatch.setattr(scan_ports, "detect_database_service_enhanced", mock_detect_db)

    # Test SSH detection (port 22)
    ssh_result = scan_ports.comprehensive_service_detection("localhost", 22)
    assert ssh_result["service"] == "SSH"
    assert "SSH-2.0" in ssh_result["version"]
    assert ssh_result["confidence"] == "high"

    # Test HTTP detection (port 80)
    http_result = scan_ports.comprehensive_service_detection("localhost", 80)
    assert http_result["service"] == "Django"
    assert http_result["confidence"] == "high"

    # Test database detection (port 5432)
    db_result = scan_ports.comprehensive_service_detection("localhost", 5432)
    assert db_result["service"] == "PostgreSQL 13.4"
    assert db_result["confidence"] == "medium"


def test_print_scan_results_rich(monkeypatch):
    scan_ports = import_scan_ports()

    # Skip if rich is not available
    if not scan_ports.HAS_RICH:
        pytest.skip("rich library not available")

    # Create test data
    open_ports = [22, 80, 443]
    closed_ports = [21, 25]
    all_ports = {22: "SSH", 80: "HTTP", 443: "HTTPS", 21: "FTP", 25: "SMTP"}
    service_results = {
        22: {
            "service": "SSH",
            "version": "OpenSSH_8.2p1",
            "confidence": "high",
            "method": "basic",
        },
        80: {
            "service": "Nginx",
            "version": "1.18.0",
            "confidence": "high",
            "method": "enhanced",
            "details": {"title": "Welcome", "server": "nginx/1.18.0", "redirect": None},
        },
    }
    config = {
        "port_lists": {
            "web": {
                "description": "Web ports",
                "ports": {"80": "HTTP", "443": "HTTPS"},
            },
            "ssh": {"description": "SSH port", "ports": {"22": "SSH"}},
        }
    }

    # Mock console.print to capture output without actually printing
    printed_outputs = []
    original_print = scan_ports.console.print

    def mock_print(*args, **kwargs):
        printed_outputs.append(args[0])
        return original_print(*args, **kwargs)

    monkeypatch.setattr(scan_ports.console, "print", mock_print)

    # Call the function
    scan_ports.print_scan_results_rich(
        open_ports, closed_ports, all_ports, service_results, config, True
    )

    # Check that something was printed
    assert len(printed_outputs) > 0

    # Reset console.print
    monkeypatch.undo()


def test_handle_list_scan(monkeypatch, capsys):
    scan_ports = import_scan_ports()

    # Create mock args
    class Args:
        host = "localhost"
        list = "web,ssh"
        timeout = 0.1
        threads = 2
        show_closed = False

    args = Args()

    # Mock dependencies
    config = {
        "port_lists": {
            "web": {
                "description": "Web ports",
                "ports": {"80": "HTTP", "443": "HTTPS"},
            },
            "ssh": {"description": "SSH port", "ports": {"22": "SSH"}},
        }
    }

    monkeypatch.setattr(scan_ports, "load_port_config", lambda: config)
    monkeypatch.setattr(
        scan_ports, "check_port", lambda host, port, timeout: port == 80
    )

    # Mock comprehensive_service_detection
    def mock_detect(host, port, timeout):
        return {
            "service": "Test Service",
            "version": "1.0",
            "confidence": "high",
            "method": "basic",
        }

    monkeypatch.setattr(scan_ports, "comprehensive_service_detection", mock_detect)

    # Call the function
    scan_ports.handle_list_scan(args, True)

    # Check output
    out = capsys.readouterr().out
    assert "Scanning" in out
    assert "80" in out
    assert "OPEN" in out


def test_handle_port_scan(monkeypatch, capsys):
    scan_ports = import_scan_ports()

    # Create mock args
    class Args:
        host = "localhost"
        port = 80
        timeout = 0.1

    args = Args()

    # Mock dependencies
    monkeypatch.setattr(scan_ports, "check_port", lambda host, port, timeout: True)

    # Mock comprehensive_service_detection
    def mock_detect(host, port, timeout):
        return {
            "service": "HTTP",
            "version": "Apache/2.4",
            "confidence": "high",
            "method": "enhanced",
        }

    monkeypatch.setattr(scan_ports, "comprehensive_service_detection", mock_detect)

    # Call the function
    scan_ports.handle_port_scan(args, True)

    # Check output
    out = capsys.readouterr().out
    assert "Checking port 80" in out
    assert "OPEN" in out
    assert "Service: HTTP" in out
    assert "Apache/2.4" in out


def test_handle_range_scan(monkeypatch, capsys):
    scan_ports = import_scan_ports()

    # Create mock args
    class Args:
        host = "localhost"
        range = (80, 85)
        timeout = 0.1
        threads = 2

    args = Args()

    # Mock dependencies to make ports 80 and 82 open
    monkeypatch.setattr(
        scan_ports, "check_port", lambda host, port, timeout: port in [80, 82]
    )

    # Call the function
    scan_ports.handle_range_scan(args)

    # Check output
    out = capsys.readouterr().out
    assert "Scanning ports 80-85" in out
    assert "80" in out  # Just check for the port number
    assert "82" in out
    assert "OPEN" in out
    assert "Summary: 2 open" in out


def test_handle_default_scan(monkeypatch):
    scan_ports = import_scan_ports()

    # Create mock args
    class Args:
        host = "localhost"
        timeout = 0.1
        show_closed = False

    args = Args()

    # Mock scan_all_configured_ports to track calls
    calls = []

    def mock_scan_all(host, timeout, show_closed, detect_services):
        calls.append((host, timeout, show_closed, detect_services))
        return [80, 443]

    monkeypatch.setattr(scan_ports, "scan_all_configured_ports", mock_scan_all)

    # Call the function with and without service detection
    scan_ports.handle_default_scan(args, True)
    assert len(calls) == 1
    assert calls[0] == ("localhost", 0.1, False, True)

    scan_ports.handle_default_scan(args, False)
    assert len(calls) == 2
    assert calls[1] == ("localhost", 0.1, False, False)


def test_log_separator_and_blank(capsys):
    scan_ports = import_scan_ports()

    scan_ports.log_separator(10)
    scan_ports.log_blank()

    out = capsys.readouterr().out
    assert "==========\n" in out
    assert "\n\n" in out  # Blank line


def test_main_with_port_arg(monkeypatch, capsys):
    scan_ports = import_scan_ports()

    # Track calls to handle_port_scan
    calls = []

    def mock_handle_port_scan(args, detect_services):
        calls.append((args.port, detect_services))

    monkeypatch.setattr(scan_ports, "handle_port_scan", mock_handle_port_scan)
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--port", "8080"])

    scan_ports.main()

    assert len(calls) == 1
    assert calls[0][0] == 8080
    assert calls[0][1] is True  # Service detection enabled by default


def test_main_with_range_arg(monkeypatch):
    scan_ports = import_scan_ports()

    # Track calls to handle_range_scan
    calls = []

    def mock_handle_range_scan(args):
        calls.append(args.range)

    monkeypatch.setattr(scan_ports, "handle_range_scan", mock_handle_range_scan)
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--range", "1000", "2000"])

    scan_ports.main()

    assert len(calls) == 1
    assert calls[0] == [1000, 2000]


def test_main_with_list_arg(monkeypatch):
    scan_ports = import_scan_ports()

    # Track calls to handle_list_scan
    calls = []

    def mock_handle_list_scan(args, detect_services):
        calls.append((args.list, detect_services))

    monkeypatch.setattr(scan_ports, "handle_list_scan", mock_handle_list_scan)
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--list", "web,database"])

    scan_ports.main()

    assert len(calls) == 1
    assert calls[0][0] == "web,database"
    assert calls[0][1] is True  # Service detection enabled by default


def test_main_with_no_service_detection(monkeypatch):
    scan_ports = import_scan_ports()

    # Track calls to handle_default_scan
    calls = []

    def mock_handle_default_scan(args, detect_services):
        calls.append(detect_services)

    monkeypatch.setattr(scan_ports, "handle_default_scan", mock_handle_default_scan)
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--no-service-detection"])

    scan_ports.main()

    assert len(calls) == 1
    assert calls[0] is False  # Service detection disabled
