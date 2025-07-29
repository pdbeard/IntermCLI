# Network Utilities

The Network Utilities module (`shared/network_utils.py`) provides common network operations with optional enhanced functionality. It handles network tasks like port scanning, service detection, and HTTP requests with graceful fallbacks.

## Key Features

- Port scanning and service detection
- HTTP requests with fallback mechanisms
- Socket operations with proper timeout handling
- Banner grabbing and service identification
- DNS resolution and validation

## Usage

### Basic Usage

```python
from shared.network_utils import NetworkUtils

# Initialize with default timeout
network = NetworkUtils()

# Check if a port is open
is_open = network.check_port("localhost", 8080)
print(f"Port 8080 is {'open' if is_open else 'closed'}")
```

### Port Scanning

```python
from shared.network_utils import NetworkUtils

# Initialize with custom timeout
network = NetworkUtils(timeout=1.0)

# Scan a range of ports
target = "example.com"
port_range = range(20, 25)
open_ports = network.scan_ports(target, port_range)

for port in open_ports:
    print(f"Port {port} is open on {target}")
```

### Service Detection

```python
from shared.network_utils import NetworkUtils

# Initialize network utilities
network = NetworkUtils()

# Detect service on a port
host = "example.com"
port = 22
banner = network.detect_service_banner(host, port)
print(f"Service on {host}:{port} - {banner}")
```

### HTTP Requests

```python
from shared.network_utils import NetworkUtils

# Initialize network utilities
network = NetworkUtils(timeout=5.0)

# Make HTTP request (uses requests if available, falls back to urllib)
url = "https://api.example.com/data"
response = network.make_http_request(url)

if response.get("success"):
    print(f"Status code: {response.get('status_code')}")
    print(f"Content: {response.get('content')}")
else:
    print(f"Error: {response.get('error')}")
```

### Enhanced HTTP with JSON

```python
from shared.network_utils import NetworkUtils

# Initialize network utilities
network = NetworkUtils()

# Make HTTP request with JSON payload
url = "https://api.example.com/data"
payload = {"key": "value"}
headers = {"Content-Type": "application/json"}

response = network.make_http_request(
    url,
    method="POST",
    data=payload,
    headers=headers,
    json=True
)

if response.get("success"):
    data = response.get("json")
    print(f"Response data: {data}")
```

### DNS Resolution

```python
from shared.network_utils import NetworkUtils

# Initialize network utilities
network = NetworkUtils()

# Resolve hostname to IP
hostname = "example.com"
ip = network.resolve_hostname(hostname)
print(f"{hostname} resolves to {ip}")

# Validate an IP address
valid = network.is_valid_ip("192.168.1.1")
print(f"IP is valid: {valid}")
```

## Methods

| Method | Description |
|--------|-------------|
| `__init__(timeout=3.0)` | Initialize network utilities with timeout |
| `check_port(host, port)` | Check if a specific port is open |
| `scan_ports(host, ports)` | Scan multiple ports and return open ones |
| `detect_service_banner(host, port)` | Attempt to get service banner from port |
| `make_http_request(url, **kwargs)` | Make HTTP request with fallback |
| `resolve_hostname(hostname)` | Resolve hostname to IP address |
| `is_valid_ip(ip)` | Check if string is valid IP address |
| `get_local_ip()` | Get local IP address |
| `ping(host, count=1)` | Ping a host and return results |

## Dependency Handling

The Network Utilities module uses progressive enhancement:

- If `requests` is available, it's used for HTTP requests
- Otherwise, it falls back to the standard library's `urllib`
- If `socket` timeout is not supported, it implements a custom timeout mechanism
- Enhanced features like async scanning are only available with appropriate dependencies

To check for dependencies, use the Enhancement Loader:

```python
from shared.enhancement_loader import EnhancementLoader

# Check for network-related dependencies
enhancements = EnhancementLoader("my-tool")
has_requests = enhancements.check_dependency("requests")
```

## Best Practices

1. **Always set reasonable timeouts** to prevent hanging on network operations
2. **Handle exceptions gracefully** and provide useful error messages
3. **Use asynchronous operations** for scanning multiple targets when appropriate
4. **Respect rate limits** when making multiple requests to the same host
5. **Validate all user input** before using in network operations

## See Also

- [Enhancement Loader](enhancement-loader.md) - For checking network-related dependencies
- [Output Handler](output-handler.md) - For displaying network operation results
