#!/usr/bin/env python3
"""
Network utilities for IntermCLI tools.
Provides common network operations with optional enhanced functionality.
"""
import logging
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Union


class NetworkUtils:
    def __init__(
        self, timeout: float = 3.0, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialize network utilities with default timeout.

        Args:
            timeout: Default timeout for network operations
            logger: Optional logger (creates one if not provided)
        """
        self.timeout = timeout
        self.logger = logger or self._get_default_logger()

        # Check for optional dependencies
        self.has_requests = self._check_module("requests")
        self.has_urllib3 = self._check_module("urllib3")
        self.has_ssl = self._check_module("ssl")

    def _get_default_logger(self) -> logging.Logger:
        """Create a basic logger if none provided."""
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
        return logging.getLogger("network_utils")

    def _check_module(self, module_name: str) -> bool:
        """
        Check if a module is available.

        Args:
            module_name: Name of the module to check

        Returns:
            True if module is available, False otherwise
        """
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    def check_port(self, host: str, port: int) -> bool:
        """
        Check if a specific port is open.

        Args:
            host: Hostname or IP address
            port: Port number to check

        Returns:
            True if port is open, False otherwise
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except (socket.error, OSError, OverflowError):
            return False

    def scan_ports(
        self, host: str, ports: List[int], max_workers: int = 10
    ) -> Dict[int, bool]:
        """
        Scan multiple ports with threading.

        Args:
            host: Hostname or IP address
            ports: List of port numbers to check
            max_workers: Maximum number of concurrent workers

        Returns:
            Dictionary of port numbers to open status
        """
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_port = {
                executor.submit(self.check_port, host, port): port for port in ports
            }
            for future in future_to_port:
                port = future_to_port[future]
                try:
                    results[port] = future.result()
                except Exception as e:
                    self.logger.debug(f"Error checking port {port}: {e}")
                    results[port] = False
        return results

    def detect_service_banner(self, host: str, port: int) -> Optional[str]:
        """
        Detect service banner on an open port.

        Args:
            host: Hostname or IP address
            port: Port number to check

        Returns:
            Service banner or None if not available
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((host, port))

                # Try with and without data
                for probe in [b"", b"GET / HTTP/1.0\r\n\r\n", b"HELP\r\n"]:
                    try:
                        if probe:
                            sock.send(probe)
                        sock.settimeout(2)
                        response = sock.recv(1024).decode("utf-8", errors="ignore")
                        if response.strip():
                            return response[:200]  # Limit response length
                    except (socket.timeout, socket.error):
                        continue
                return None
        except Exception as e:
            self.logger.debug(f"Error detecting service banner on {host}:{port}: {e}")
            return None

    def detect_http_service(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Detect HTTP service with enhanced info if requests is available.

        Args:
            host: Hostname or IP address
            port: Port number to check

        Returns:
            Dictionary of HTTP service details or None if not an HTTP service
        """
        if self.has_requests:
            return self._detect_http_enhanced(host, port)
        return self._detect_http_basic(host, port)

    def _detect_http_basic(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Basic HTTP detection using standard library.

        Args:
            host: Hostname or IP address
            port: Port number to check

        Returns:
            Dictionary of HTTP service details or None if not an HTTP service
        """
        protocols = ["http"]
        if port in [443, 8443] and self.has_ssl:
            protocols = ["https", "http"]

        for protocol in protocols:
            try:
                import urllib.error
                import urllib.request

                url = f"{protocol}://{host}:{port}"
                req = urllib.request.Request(
                    url, headers={"User-Agent": "IntermCLI/1.0"}
                )

                # Create context for HTTPS
                if protocol == "https" and self.has_ssl:
                    import ssl

                    ctx = ssl.create_default_context()
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                    response = urllib.request.urlopen(
                        req, timeout=self.timeout, context=ctx
                    )
                else:
                    response = urllib.request.urlopen(req, timeout=self.timeout)

                content = response.read().decode("utf-8", errors="ignore")
                headers = dict(response.headers)

                return {
                    "protocol": protocol,
                    "status_code": response.status,
                    "server": headers.get("Server", "Unknown"),
                    "title": self._extract_title(content),
                    "content_type": headers.get("Content-Type", "Unknown"),
                }
            except (urllib.error.URLError, socket.timeout, ConnectionRefusedError):
                continue
            except Exception as e:
                self.logger.debug(
                    f"Error with basic HTTP detection on {host}:{port}: {e}"
                )
                continue

        return None

    def _detect_http_enhanced(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """
        Enhanced HTTP detection using requests.

        Args:
            host: Hostname or IP address
            port: Port number to check

        Returns:
            Dictionary of HTTP service details or None if not an HTTP service
        """
        import requests

        if self.has_urllib3:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        protocols = ["http"]
        if port in [443, 8443]:
            protocols = ["https", "http"]

        for protocol in protocols:
            try:
                url = f"{protocol}://{host}:{port}"
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    verify=False,
                    allow_redirects=False,
                    headers={"User-Agent": "IntermCLI/1.0"},
                )

                return {
                    "protocol": protocol,
                    "status_code": response.status_code,
                    "server": response.headers.get("Server", "Unknown"),
                    "content_type": response.headers.get("Content-Type", "Unknown"),
                    "title": self._extract_title(response.text),
                    "redirect": response.headers.get("Location"),
                    "response_time": response.elapsed.total_seconds(),
                }
            except requests.RequestException:
                continue
            except Exception as e:
                self.logger.debug(
                    f"Error with enhanced HTTP detection on {host}:{port}: {e}"
                )
                continue

        return None

    def _extract_title(self, html_content: str) -> Optional[str]:
        """
        Extract title from HTML content.

        Args:
            html_content: HTML content to extract title from

        Returns:
            Title string or None if not found
        """
        match = re.search(r"<title[^>]*>([^<]+)</title>", html_content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    def get_hostname(self, ip: str) -> Optional[str]:
        """
        Get hostname from IP address.

        Args:
            ip: IP address to look up

        Returns:
            Hostname or None if not found
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            return None

    def get_ip(self, hostname: str) -> Optional[str]:
        """
        Get IP address from hostname.

        Args:
            hostname: Hostname to look up

        Returns:
            IP address or None if not found
        """
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            return None

    def make_http_request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with fallback between requests and urllib.

        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            headers: Optional request headers
            data: Optional request data (form data or raw)
            json_data: Optional JSON data (will set Content-Type)
            timeout: Optional timeout (overrides default)

        Returns:
            Dictionary with response details
        """
        if self.has_requests:
            return self._make_request_enhanced(
                url, method, headers, data, json_data, timeout
            )
        return self._make_request_basic(url, method, headers, data, json_data, timeout)

    def _make_request_basic(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request using urllib (stdlib only).

        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            headers: Optional request headers
            data: Optional request data (form data or raw)
            json_data: Optional JSON data (will set Content-Type)
            timeout: Optional timeout (overrides default)

        Returns:
            Dictionary with response details
        """
        import json
        import urllib.error
        import urllib.request

        timeout = timeout or self.timeout
        headers = headers or {}

        # Process request data
        request_data = None
        if json_data:
            request_data = json.dumps(json_data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif data:
            if isinstance(data, dict):
                import urllib.parse

                request_data = urllib.parse.urlencode(data).encode("utf-8")
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            elif isinstance(data, str):
                request_data = data.encode("utf-8")
            else:
                request_data = data

        # Create request
        req = urllib.request.Request(
            url, data=request_data, headers=headers, method=method
        )

        start_time = time.time()
        try:
            # Handle SSL verification
            if url.startswith("https") and self.has_ssl:
                import ssl

                ctx = ssl.create_default_context()
                response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
            else:
                response = urllib.request.urlopen(req, timeout=timeout)

            # Process response
            content = response.read()
            elapsed = time.time() - start_time
            headers_dict = dict(response.headers)

            # Try to parse JSON response
            json_response = None
            if "application/json" in headers_dict.get("Content-Type", ""):
                try:
                    json_response = json.loads(content.decode("utf-8"))
                except json.JSONDecodeError:
                    pass

            return {
                "status_code": response.status,
                "headers": headers_dict,
                "content": content,
                "text": content.decode("utf-8", errors="ignore"),
                "elapsed": elapsed,
                "url": response.url,
                "json": json_response,
            }

        except urllib.error.HTTPError as e:
            # Handle HTTP errors (4xx, 5xx)
            content = e.read()
            elapsed = time.time() - start_time

            # Try to parse JSON response
            json_response = None
            if "application/json" in e.headers.get("Content-Type", ""):
                try:
                    json_response = json.loads(content.decode("utf-8"))
                except json.JSONDecodeError:
                    pass

            return {
                "status_code": e.code,
                "headers": dict(e.headers),
                "content": content,
                "text": content.decode("utf-8", errors="ignore"),
                "elapsed": elapsed,
                "url": url,
                "error": str(e),
                "json": json_response,
            }

        except Exception as e:
            # Handle other errors (connection, timeout, etc.)
            elapsed = time.time() - start_time
            return {
                "status_code": -1,
                "headers": {},
                "content": b"",
                "text": "",
                "elapsed": elapsed,
                "url": url,
                "error": str(e),
                "json": None,
            }

    def _make_request_enhanced(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Union[Dict, str, bytes]] = None,
        json_data: Optional[Dict] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request using requests library.

        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            headers: Optional request headers
            data: Optional request data (form data or raw)
            json_data: Optional JSON data (will set Content-Type)
            timeout: Optional timeout (overrides default)

        Returns:
            Dictionary with response details
        """
        import requests

        timeout = timeout or self.timeout
        headers = headers or {}

        # Disable insecure request warnings
        if self.has_urllib3:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                json=json_data,
                timeout=timeout,
                verify=False,
            )

            json_response = None
            try:
                json_response = response.json()
            except (ValueError, requests.exceptions.JSONDecodeError):
                pass

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
                "text": response.text,
                "elapsed": response.elapsed.total_seconds(),
                "url": response.url,
                "json": json_response,
                "cookies": dict(response.cookies),
                "encoding": response.encoding,
                "history": [r.url for r in response.history],
            }

        except requests.RequestException as e:
            # Handle request exceptions
            return {
                "status_code": -1,
                "headers": {},
                "content": b"",
                "text": "",
                "elapsed": 0,
                "url": url,
                "error": str(e),
                "json": None,
            }


def create_network_utils(
    timeout: float = 3.0, logger: Optional[logging.Logger] = None
) -> NetworkUtils:
    """
    Helper function to create a network utilities instance.

    Args:
        timeout: Default timeout for network operations
        logger: Optional logger

    Returns:
        NetworkUtils instance
    """
    return NetworkUtils(timeout, logger)
