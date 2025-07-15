import sys
import os
import tempfile
import types
import pytest
import json
import importlib.util

# Dynamically import the test-endpoints tool as a module
TOOL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tools/test-endpoints/test-endpoints.py'))
spec = importlib.util.spec_from_file_location("test_endpoints", TOOL_PATH)
test_endpoints = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test_endpoints)

class DummyResponse:
    def __init__(self, status_code=200, text='{"ok":true}', headers=None, elapsed=0.1):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {"Content-Type": "application/json"}
        self.elapsed = elapsed

def test_format_json_valid():
    data = '{"foo": "bar"}'
    formatted = test_endpoints.format_json(data)
    assert formatted.startswith('{\n  "foo"')

def test_format_json_invalid():
    data = 'not json'
    formatted = test_endpoints.format_json(data)
    assert formatted == 'not json'

def test_substitute_variables():
    text = "Hello {{name}}!"
    variables = {"name": "World"}
    result = test_endpoints.substitute_variables(text, variables)
    assert result == "Hello World!"

def test_make_request_simple(monkeypatch):
    # Patch urllib.request.urlopen to return a dummy response
    class DummyHTTPResponse:
        def getcode(self): return 200
        @property
        def headers(self): return {"Content-Type": "application/json"}
        def read(self): return b'{"ok":true}'

    monkeypatch.setattr(test_endpoints.urllib.request, "urlopen", lambda req, timeout=30: DummyHTTPResponse())
    resp = test_endpoints.make_request_simple("GET", "https://example.com")
    assert resp.status_code == 200
    assert json.loads(resp.text)["ok"] is True

def test_print_response_simple(capsys):
    resp = DummyResponse()
    test_endpoints.print_response_simple(resp)
    out = capsys.readouterr().out
    assert "✅ 200" in out
    assert "Body:" in out
    assert "{\n  \"ok\": true\n}" in out

def test_check_dependencies(capsys):
    test_endpoints.check_dependencies()
    out = capsys.readouterr().out
    assert "Dependency Status" in out
    assert "requests" in out

def test_load_collection(tmp_path):
    toml_content = b"[request]\nname = 'Test'\nurl = 'https://example.com'\n"
    toml_file = tmp_path / "collection.toml"
    toml_file.write_bytes(toml_content)
    if test_endpoints.tomllib:
        result = test_endpoints.load_collection(str(toml_file))
        assert "request" in result
    else:
        assert test_endpoints.load_collection(str(toml_file)) is None

def test_main_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["test-endpoints.py"])
    test_endpoints.main()
    out = capsys.readouterr().out
    assert "usage" in out.lower()
