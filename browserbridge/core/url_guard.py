"""
Navigation URL SSRF validator.
Blocks loopback, RFC1918 private networks, link-local cloud metadata (169.254.169.254),
and non-HTTP(S) schemes unless BROWSERBRIDGE_ALLOW_PRIVATE_URLS=1 is explicitly set.
"""
import ipaddress
import os
import re
import socket
from urllib.parse import urlparse

_BLOCKED_HOSTS = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
    "metadata.google.internal",
    "metadata",
}
_NUMERIC_HOST_RE = re.compile(r"^(0x[0-9a-f]+|\d+(\.\d+){0,3})$", re.IGNORECASE)


def _is_forbidden_ip(ip_obj: ipaddress._BaseAddress) -> bool:
    return (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def validate_navigation_url(url: str) -> str:
    """Validate and return normalized HTTP(S) URL, raising ValueError if unsafe."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Navigation URL must be a non-empty string.")

    raw = url.strip()
    if "://" not in raw:
        raw = f"https://{raw}"

    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Blocked URL scheme '{parsed.scheme}': only http and https are allowed.")

    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        raise ValueError("Invalid URL: missing hostname.")

    if os.getenv("BROWSERBRIDGE_ALLOW_PRIVATE_URLS", "").strip() in ("1", "true", "yes"):
        return raw

    if host in _BLOCKED_HOSTS or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError(f"Blocked target host '{host}': internal or loopback addresses are forbidden.")

    try:
        ip_obj = ipaddress.ip_address(host)
        if _is_forbidden_ip(ip_obj):
            raise ValueError(f"Blocked target IP '{ip_obj}': non-public address range.")
        return raw
    except ValueError as exc:
        if "Blocked target IP" in str(exc):
            raise

    if _NUMERIC_HOST_RE.match(host):
        try:
            packed = socket.inet_aton(host)
            ip_obj = ipaddress.IPv4Address(packed)
            if _is_forbidden_ip(ip_obj):
                raise ValueError(f"Blocked target numeric IP '{ip_obj}': non-public address range.")
        except OSError as exc:
            raise ValueError(f"Blocked malformed numeric host '{host}'.") from exc

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return raw

    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        addr_str = sockaddr[0].split("%", 1)[0]
        try:
            ip_obj = ipaddress.ip_address(addr_str)
        except ValueError:
            continue
        if _is_forbidden_ip(ip_obj):
            raise ValueError(f"Blocked target host '{host}': resolves to non-public IP '{ip_obj}'.")

    return raw
