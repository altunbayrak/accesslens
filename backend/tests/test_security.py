import socket
import pytest
from app.security import UnsafeTarget, validate_target

def resolved_public(*args, **kwargs): return [(None, None, None, None, ("93.184.216.34", 443))]
def test_allows_authorized_public_domain(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", resolved_public)
    assert validate_target("https://docs.example.com/a", ["example.com"]).startswith("https://")
@pytest.mark.parametrize("url", ["http://127.0.0.1", "http://169.254.169.254/latest/meta-data", "file:///etc/passwd"])
def test_blocks_unsafe_scheme_or_ip(monkeypatch, url):
    monkeypatch.setattr(socket, "getaddrinfo", resolved_public)
    with pytest.raises(UnsafeTarget): validate_target(url, ["example.com"])
def test_blocks_private_dns(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", lambda *x, **y: [(None,None,None,None,("10.0.0.8", 443))])
    with pytest.raises(UnsafeTarget): validate_target("https://example.com", ["example.com"])
def test_blocks_unapproved_domain(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", resolved_public)
    with pytest.raises(UnsafeTarget): validate_target("https://evil.example", ["example.com"])
