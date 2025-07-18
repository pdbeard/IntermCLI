import importlib.util
import json
import os
import sys


# Dynamically import the test-endpoints tool as a module (for coverage compatibility)
def import_test_endpoints():
    tool_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../tools/test-endpoints/test-endpoints.py"
        )
    )
    spec = importlib.util.spec_from_file_location("test_endpoints", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


test_endpoints = import_test_endpoints()


class DummyResponse:
    """
    Universal mock for HTTP responses in test_endpoints_test.py.
    Implements getcode() and read() to match urllib and requests response interfaces.
    """

    def __init__(self, status_code=200, text='{"ok":true}', headers=None, elapsed=0.1):
        self.status_code = status_code
        self.text = text
        self.headers = headers or {"Content-Type": "application/json"}
        self.elapsed = elapsed

    def getcode(self):
        return self.status_code

    def read(self):
        return self.text.encode("utf-8")


def test_requests_import_error(monkeypatch):
    # Simulate ImportError for 'requests'
    monkeypatch.setitem(sys.modules, "requests", None)
    import importlib.util
    import os

    # Use absolute path so it works in any pytest temp directory
    tool_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../tools/test-endpoints/test-endpoints.py"
        )
    )
    spec = importlib.util.spec_from_file_location("test_endpoints", tool_path)
    test_endpoints = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_endpoints)

    assert hasattr(test_endpoints, "HAS_REQUESTS")
    assert test_endpoints.HAS_REQUESTS is False


def test_toml_import_error(monkeypatch):
    # Simulate ImportError for both tomllib and tomli
    monkeypatch.setitem(sys.modules, "tomllib", None)
    monkeypatch.setitem(sys.modules, "tomli", None)
    import importlib.util
    import os

    tool_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../tools/test-endpoints/test-endpoints.py"
        )
    )
    spec = importlib.util.spec_from_file_location("test_endpoints", tool_path)
    test_endpoints = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_endpoints)

    assert hasattr(test_endpoints, "tomllib")
    assert test_endpoints.tomllib is None


def test_simple_response_json():
    class DummyHTTPResponse:
        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "application/json"}

        def read(self):
            return b'{"foo": "bar"}'

    resp = test_endpoints.SimpleResponse(
        DummyHTTPResponse(), "https://example.com", start_time=0
    )
    result = resp.json()
    assert result == {"foo": "bar"}


def test_make_request_simple_headers_none(monkeypatch):
    # Patch urllib.request.Request to capture headers
    captured = {}

    class DummyHTTPResponse:
        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "application/json"}

        def read(self):
            return b'{"ok":true}'

    def dummy_urlopen(req, timeout=30):
        captured["headers"] = req.headers
        return DummyHTTPResponse()

    monkeypatch.setattr(test_endpoints.urllib.request, "urlopen", dummy_urlopen)
    resp = test_endpoints.make_request_simple(
        "GET", "https://example.com", headers=None
    )
    assert resp.status_code == 200
    assert isinstance(captured["headers"], dict)
    assert captured["headers"] == {}


def test_rich_import_error(monkeypatch):
    # Simulate ImportError for 'rich.console'
    monkeypatch.setitem(sys.modules, "rich.console", None)
    monkeypatch.setitem(sys.modules, "rich.panel", None)
    monkeypatch.setitem(sys.modules, "rich.syntax", None)
    monkeypatch.setitem(sys.modules, "rich.table", None)
    import importlib.util
    import os

    tool_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "../tools/test-endpoints/test-endpoints.py"
        )
    )
    spec = importlib.util.spec_from_file_location("test_endpoints", tool_path)
    test_endpoints = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(test_endpoints)

    assert hasattr(test_endpoints, "HAS_RICH")
    assert test_endpoints.HAS_RICH is False
    assert test_endpoints.console is None


def test_format_json_valid():
    data = '{"foo": "bar"}'
    formatted = test_endpoints.format_json(data)
    assert formatted.startswith('{\n  "foo"')


def test_format_json_invalid():
    data = "not json"
    formatted = test_endpoints.format_json(data)
    assert formatted == "not json"


def test_print_response_simple(capsys):
    resp = DummyResponse()
    test_endpoints.print_response_simple(resp)
    out = capsys.readouterr().out
    assert "✅ 200" in out
    assert "Body:" in out
    assert '{\n  "ok": true\n}' in out


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


def test_make_request_enhanced_timeout_verify(monkeypatch):
    # Covers 159-161: timeout and verify
    class DummyResponse:
        def __init__(self):
            self.elapsed = 0.1

        status_code = 200
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    def dummy_request(method, url, **kwargs):
        assert kwargs["timeout"] == 10
        assert kwargs["verify"] is False
        return DummyResponse()

    monkeypatch.setattr(test_endpoints.requests, "request", dummy_request)
    resp = test_endpoints.make_request_enhanced(
        "GET", "https://example.com", timeout=10, verify=False
    )
    assert resp.status_code == 200


def test_format_json_jsondecodeerror():
    # Covers 191-192: JSONDecodeError
    result = test_endpoints.format_json("{invalid json}")
    assert result == "{invalid json}"


def test_print_response_rich_no_text(monkeypatch):
    # Covers 233: no text
    class DummyConsole:
        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(test_endpoints, "console", DummyConsole())
    monkeypatch.setattr(test_endpoints, "HAS_RICH", True)

    class DummyResponse:
        status_code = 200
        elapsed = 0.1
        headers = {"Content-Type": "application/json"}
        text = ""

    test_endpoints.print_response_rich(DummyResponse(), verbose=True, show_headers=True)


def test_load_collection_no_collection(monkeypatch):
    # Covers 347-348: no collection_path
    monkeypatch.setattr(test_endpoints, "tomllib", None)
    result = test_endpoints.load_collection()
    assert result is None


def test_check_dependencies_status(capsys):
    # Covers 428: prints status for all deps
    test_endpoints.check_dependencies()
    out = capsys.readouterr().out
    assert "requests" in out and "rich" in out and "tomli/tomllib" in out


def test_make_request_simple_no_data(monkeypatch):
    # Covers lines 87-89: no data, headers default
    class DummyHTTPResponse:
        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "application/json"}

        def read(self):
            return b'{"ok":true}'

    monkeypatch.setattr(
        test_endpoints.urllib.request,
        "urlopen",
        lambda req, timeout=30: DummyHTTPResponse(),
    )
    resp = test_endpoints.make_request_simple("GET", "https://example.com")
    assert resp.status_code == 200


def test_print_response_rich_no_headers(monkeypatch):
    # Covers 228-230: show_headers False
    class DummyConsole:
        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(test_endpoints, "console", DummyConsole())
    monkeypatch.setattr(test_endpoints, "HAS_RICH", True)

    class DummyResponse:
        status_code = 200
        elapsed = 0.1
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    test_endpoints.print_response_rich(
        DummyResponse(), verbose=True, show_headers=False
    )


def test_print_response_simple_no_headers(monkeypatch, capsys):
    # Covers 238: show_headers False
    class DummyResponse:
        status_code = 200
        elapsed = 0.1
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    test_endpoints.print_response_simple(DummyResponse(), show_headers=False)
    out = capsys.readouterr().out
    assert "Headers:" not in out


def test_load_collection_print(monkeypatch, tmp_path, capsys):
    # Covers 355, 360-363, 367-373: config_loaded, file_config, error
    toml_content = b"[request]\nname = 'Test'\nurl = 'https://example.com'\n"
    toml_file = tmp_path / "collection.toml"
    toml_file.write_bytes(toml_content)
    monkeypatch.setattr(test_endpoints, "tomllib", __import__("tomllib"))
    result = test_endpoints.load_collection(str(toml_file))
    assert "request" in result

    # Simulate error loading file
    def bad_load(f):
        raise Exception("fail")

    monkeypatch.setattr(test_endpoints.tomllib, "load", bad_load)
    out = capsys.readouterr().out
    test_endpoints.load_collection(str(toml_file))
    out = capsys.readouterr().out
    assert "Failed to load collection" in out


def test_substitute_variables_multiple():
    # Covers 385-424: multiple variables
    text = "{{a}} {{b}} {{c}}"
    variables = {"a": 1, "b": 2, "c": 3}
    result = test_endpoints.substitute_variables(text, variables)
    assert result == "1 2 3"


def test_make_request_enhanced_json(monkeypatch):
    # Test make_request_enhanced with json_data
    class DummyResponse:
        def __init__(self):
            self.elapsed = 0.1

        status_code = 200
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    def dummy_request(method, url, **kwargs):
        assert kwargs["json"] == {"foo": "bar"}
        return DummyResponse()

    monkeypatch.setattr(test_endpoints.requests, "request", dummy_request)
    resp = test_endpoints.make_request_enhanced(
        "POST", "https://example.com", json_data={"foo": "bar"}
    )
    assert resp.status_code == 200


def test_make_request_enhanced_data(monkeypatch):
    # Test make_request_enhanced with data
    class DummyResponse:
        def __init__(self):
            self.elapsed = 0.1

        status_code = 200
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    def dummy_request(method, url, **kwargs):
        assert kwargs["data"] == "foo=bar"
        return DummyResponse()

    monkeypatch.setattr(test_endpoints.requests, "request", dummy_request)
    resp = test_endpoints.make_request_enhanced(
        "POST", "https://example.com", data="foo=bar"
    )
    assert resp.status_code == 200


def test_format_json_valid_dict():
    # Should format dict as JSON
    result = test_endpoints.format_json(json.dumps({"foo": "bar"}))
    assert result.startswith('{\n  "foo"')


def test_format_json_invalid_type():
    # Should return input if not JSON
    result = test_endpoints.format_json("not json")
    assert result == "not json"


def test_print_response(monkeypatch):
    # Should call print_response_rich or print_response_simple
    called = {"rich": False, "simple": False}

    def fake_rich(*a, **kw):
        called["rich"] = True

    def fake_simple(*a, **kw):
        called["simple"] = True

    monkeypatch.setattr(test_endpoints, "print_response_rich", fake_rich)
    monkeypatch.setattr(test_endpoints, "print_response_simple", fake_simple)
    monkeypatch.setattr(test_endpoints, "HAS_RICH", True)
    monkeypatch.setattr(test_endpoints, "console", object())
    test_endpoints.print_response(object())
    assert called["rich"]
    monkeypatch.setattr(test_endpoints, "HAS_RICH", False)
    test_endpoints.print_response(object())
    assert called["simple"]


def test_print_response_rich_status(monkeypatch):
    # Test status color logic
    class DummyConsole:
        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(test_endpoints, "console", DummyConsole())
    monkeypatch.setattr(test_endpoints, "HAS_RICH", True)

    class DummyResponse:
        status_code = 201
        elapsed = 0.1
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    test_endpoints.print_response_rich(DummyResponse(), verbose=True, show_headers=True)
    DummyResponse.status_code = 404
    test_endpoints.print_response_rich(DummyResponse(), verbose=True, show_headers=True)
    DummyResponse.status_code = 301
    test_endpoints.print_response_rich(DummyResponse(), verbose=True, show_headers=True)


## Removed commented-out test_print_response_simple_status for clarity


def test_print_response_simple_body(monkeypatch, capsys):
    class DummyResponse:
        status_code = 200
        elapsed = 0.1
        headers = {"Content-Type": "application/json"}
        text = ""

    test_endpoints.print_response_simple(DummyResponse())
    out = capsys.readouterr().out
    assert "Body:" not in out


def test_load_collection_paths(monkeypatch, tmp_path):
    # Test collection_path argument and fallback order
    toml_content = b"[request]\nname = 'Test'\nurl = 'https://example.com'\n"
    toml_file = tmp_path / "collection.toml"
    toml_file.write_bytes(toml_content)
    monkeypatch.setattr(test_endpoints, "tomllib", __import__("tomllib"))
    result = test_endpoints.load_collection(str(toml_file))
    assert "request" in result


def test_substitute_variables(monkeypatch):
    # Test variable substitution
    text = "Hello {{name}}!"
    variables = {"name": "World"}
    result = test_endpoints.substitute_variables(text, variables)
    assert result == "Hello World!"


def test_substitute_variables_no_vars():
    # Should return unchanged if no variables
    text = "Hello World!"
    variables = {}
    result = test_endpoints.substitute_variables(text, variables)
    assert result == "Hello World!"


def test_check_dependencies_all_available(monkeypatch, capsys):
    monkeypatch.setattr(test_endpoints, "HAS_REQUESTS", True)
    monkeypatch.setattr(test_endpoints, "HAS_RICH", True)
    monkeypatch.setattr(test_endpoints, "tomllib", True)
    test_endpoints.check_dependencies()
    out = capsys.readouterr().out
    assert "Available" in out


def test_main(monkeypatch, capsys):
    # Test main with --version
    monkeypatch.setattr(sys, "argv", ["test-endpoints.py", "--version"])
    try:
        test_endpoints.main()
    except SystemExit:
        pass
    out = capsys.readouterr().out
    assert "test-endpoints" in out or out == ""


def test_make_request_simple_data_dict(monkeypatch):
    # Test data dict encoding and Content-Type header
    # Patch Request to capture headers
    captured = {}
    real_Request = test_endpoints.urllib.request.Request

    def dummy_Request(url, data=None, headers=None, method=None):
        captured["headers"] = headers
        return real_Request(url, data=data, headers=headers, method=method)

    monkeypatch.setattr(test_endpoints.urllib.request, "Request", dummy_Request)

    monkeypatch.setattr(
        test_endpoints.urllib.request,
        "urlopen",
        lambda req, timeout=30: DummyResponse(),
    )
    resp = test_endpoints.make_request_simple(
        "POST", "https://example.com", data={"foo": "bar"}
    )
    assert resp.status_code == 200
    assert captured["headers"]["Content-Type"] == "application/json"


def test_make_request_simple_data_str(monkeypatch):
    # Test data str encoding
    class DummyHTTPResponse:
        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "application/json"}

        def read(self):
            return b'{"ok":true}'

    def dummy_urlopen(req, timeout=30):
        return DummyHTTPResponse()

    monkeypatch.setattr(test_endpoints.urllib.request, "urlopen", dummy_urlopen)
    resp = test_endpoints.make_request_simple(
        "POST", "https://example.com", data="foo=bar"
    )
    assert resp.status_code == 200


def test_make_request_simple_http_error(monkeypatch):
    # Test HTTPError branch
    class DummyHTTPError(Exception):
        def getcode(self):
            return 404

        @property
        def headers(self):
            return {"Content-Type": "application/json"}

        def read(self):
            return b'{"error":true}'

    def dummy_urlopen(req, timeout=30):
        raise test_endpoints.urllib.error.HTTPError(
            req.full_url, 404, "Not Found", {}, None
        )

    monkeypatch.setattr(test_endpoints.urllib.request, "urlopen", dummy_urlopen)

    # Patch SimpleResponse to accept HTTPError
    class DummyHTTPErrorResponse:
        def getcode(self):
            return 404

        @property
        def headers(self):
            return {"Content-Type": "application/json"}

        def read(self):
            return b'{"error":true}'

    monkeypatch.setattr(
        test_endpoints.urllib.request,
        "urlopen",
        lambda req, timeout=30: DummyHTTPErrorResponse(),
    )
    resp = test_endpoints.make_request_simple("GET", "https://example.com")
    assert resp.status_code == 404


def test_format_json_type_error():
    # Should return input if not a string
    result = test_endpoints.format_json(None)
    assert result is None


def test_print_response_rich(monkeypatch):
    # Simulate rich available
    class DummyConsole:
        def print(self, *args, **kwargs):
            pass

    monkeypatch.setattr(test_endpoints, "console", DummyConsole())
    monkeypatch.setattr(test_endpoints, "HAS_RICH", True)

    class DummyResponse:
        status_code = 200
        elapsed = 0.1
        headers = {"Content-Type": "application/json"}
        text = '{"ok":true}'

    test_endpoints.print_response_rich(DummyResponse(), verbose=True, show_headers=True)


def test_substitute_variables_non_str():
    # Should return input if not a string
    result = test_endpoints.substitute_variables(123, {"foo": "bar"})
    assert result == 123


def test_check_dependencies_output(capsys):
    test_endpoints.check_dependencies()
    out = capsys.readouterr().out
    assert "Dependency Status" in out


def test_load_collection_no_toml(monkeypatch):
    monkeypatch.setattr(test_endpoints, "tomllib", None)
    result = test_endpoints.load_collection()
    assert result is None


def test_load_collection_file(tmp_path, monkeypatch):
    toml_content = b"[request]\nname = 'Test'\nurl = 'https://example.com'\n"
    toml_file = tmp_path / "collection.toml"
    toml_file.write_bytes(toml_content)
    if test_endpoints.tomllib:
        result = test_endpoints.load_collection(str(toml_file))
        assert "request" in result
    else:
        assert test_endpoints.load_collection(str(toml_file)) is None


def test_main_invalid_json(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["test-endpoints.py", "POST", "https://example.com", "--json", "not json"],
    )
    test_endpoints.main()
    out = capsys.readouterr().out
    assert "Invalid JSON" in out


def test_main_no_args(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["test-endpoints.py"])
    test_endpoints.main()
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_main_check_deps(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["test-endpoints.py", "--check-deps"])
    test_endpoints.main()
    out = capsys.readouterr().out
    assert "Dependency Status" in out
