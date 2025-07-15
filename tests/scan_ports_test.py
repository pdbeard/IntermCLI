import sys
import os
import pytest
import importlib.util

# Dynamically import the scan-ports tool as a module
TOOL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools/scan-ports/scan-ports.py'))
spec = importlib.util.spec_from_file_location("scan_ports", TOOL_PATH)
scan_ports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan_ports)

def test_check_optional_dependencies():
    deps, missing = scan_ports.check_optional_dependencies()
    assert isinstance(deps, dict)
    assert "requests" in deps

def test_print_dependency_status(capsys):
    scan_ports.print_dependency_status(verbose=True)
    out = capsys.readouterr().out
    assert "Optional Dependencies Status" in out

def test_load_port_config_default():
    config = scan_ports.load_port_config()
    assert "port_lists" in config
    assert "common" in config["port_lists"]

def test_list_available_port_lists(capsys):
    scan_ports.list_available_port_lists()
    out = capsys.readouterr().out
    assert "Available Port Lists" in out

def test_get_ports_from_lists():
    config = scan_ports.load_port_config()
    ports = scan_ports.get_ports_from_lists(["common"], config)
    assert isinstance(ports, dict)
    assert 22 in ports
    assert ports[22] == "SSH"

def test_get_ports_from_lists_all():
    config = scan_ports.load_port_config()
    ports = scan_ports.get_ports_from_lists(["all"], config)
    assert isinstance(ports, dict)
    assert 22 in ports
    assert 80 in ports

def test_check_port_closed():
    # Use a high port that is almost always closed
    assert scan_ports.check_port("localhost", 65000, timeout=0.1) is False

def test_check_port_open(monkeypatch):
    # Patch socket to simulate open port
    import socket
    class DummySocket:
        def __init__(self, *a, **kw): pass
        def settimeout(self, t): pass
        def connect_ex(self, addr): return 0
        def __enter__(self): return self
        def __exit__(self, *a): pass
    monkeypatch.setattr(socket, "socket", lambda *a, **kw: DummySocket())
    assert scan_ports.check_port("localhost", 22, timeout=0.1) is True

def test_main_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["scan-ports.py", "--help"])
    with pytest.raises(SystemExit):
        scan_ports.main()
    out = capsys.readouterr().out
    assert "usage" in out.lower()
