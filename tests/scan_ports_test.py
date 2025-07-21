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
