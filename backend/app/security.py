"""Network boundary checks. Always call before every outbound navigation/request."""
import ipaddress
import socket
from urllib.parse import urlparse

BLOCKED_HOSTS = {"metadata.google.internal", "metadata", "instance-data", "169.254.169.254"}


class UnsafeTarget(ValueError):
    pass


def _unsafe_ip(value: str) -> bool:
    ip = ipaddress.ip_address(value)
    return any((ip.is_private, ip.is_loopback, ip.is_link_local, ip.is_multicast, ip.is_unspecified, ip.is_reserved))


def validate_target(url: str, allowed_domains: list[str]) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeTarget("Only unauthenticated HTTP(S) URLs are allowed")
    host = parsed.hostname.rstrip(".").lower()
    if host in BLOCKED_HOSTS or host.endswith(".internal"):
        raise UnsafeTarget("Metadata or internal host is blocked")
    if not any(host == d or host.endswith("." + d) for d in allowed_domains):
        raise UnsafeTarget("Host is not on this project's authorized domain allowlist")
    try:
        addresses = {row[4][0] for row in socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        raise UnsafeTarget("Target host cannot be resolved") from exc
    if not addresses or any(_unsafe_ip(address) for address in addresses):
        raise UnsafeTarget("Target resolves to a prohibited network address")
    return parsed.geturl()
