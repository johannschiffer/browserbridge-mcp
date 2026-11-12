"""
Connect-time SSRF guard.
Resolves the target host once, validates every resolved address and connects to the
validated IP, so DNS rebinding between validation and connection cannot reach private
networks. TLS SNI and the Host header keep the original hostname.
"""
import os
import socket
from typing import Optional

import httpcore
import httpx

from .url_guard import _is_forbidden_ip
import ipaddress

_ALLOW_ENV = "BROWSERBRIDGE_ALLOW_PRIVATE_URLS"


def _allow_private() -> bool:
    return os.getenv(_ALLOW_ENV, "").strip() in ("1", "true", "yes")


class _GuardedBackend(httpcore.SyncBackend):
    def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        target = host
        if not _allow_private():
            infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            chosen: Optional[str] = None
            for info in infos:
                addr = info[4][0].split("%", 1)[0]
                ip_obj = ipaddress.ip_address(addr)
                if _is_forbidden_ip(ip_obj):
                    raise httpcore.ConnectError(
                        f"Blocked connection to '{host}': resolves to non-public IP '{ip_obj}'."
                    )
                if chosen is None:
                    chosen = addr
            if chosen is None:
                raise httpcore.ConnectError(f"Could not resolve '{host}'.")
            target = chosen
        return super().connect_tcp(
            target, port, timeout=timeout, local_address=local_address, socket_options=socket_options
        )


def guarded_transport(**kwargs) -> httpx.HTTPTransport:
    """HTTPTransport whose TCP connections are validated against non-public IP ranges."""
    transport = httpx.HTTPTransport(**kwargs)
    pool = getattr(transport, "_pool", None)
    if pool is not None and hasattr(pool, "_network_backend"):
        pool._network_backend = _GuardedBackend()
    return transport
