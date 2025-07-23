import re
from typing import Any, Dict


# Dummy stubs for undefined functions
def detect_ssh_service(host, port, timeout):
    return None


def detect_http_service(host, port, timeout):
    return None


def detect_database_service(host, port, timeout):
    return None


def detect_service_banner(host, port, timeout):
    return None


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
    result = {
        "service": common_ports.get(port, "Unknown"),
        "version": None,
        "confidence": "low",
        "method": "basic",
        "details": None,
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
        http_info = detect_http_service(host, port, timeout)
        if http_info:
            # Determine the service name
            if http_info.get("framework"):
                service_name = http_info["framework"]
            elif http_info.get("server") and http_info["server"] != "Unknown":
                service_name = http_info["server"].split("/")[0]
            else:
                service_name = "HTTP" if http_info["protocol"] == "http" else "HTTPS"

            # Build the result
            result["service"] = service_name
            result["version"] = http_info.get("server", "").replace(
                service_name + "/", ""
            )
            result["confidence"] = "high"
            # Remove reference to network_utils, just use 'basic' for scratchpad
            result["method"] = "basic"
            result["details"] = http_info
            return result

    # Try database detection for common database ports
    if port in [3306, 5432, 6379, 27017, 9200, 5984, 8086]:
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
