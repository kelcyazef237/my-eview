"""Tests for the TLS collector.

These tests exercise the live `_handshake_info` function against a real
TLS endpoint. They are skipped automatically when the network or DNS is
unreachable, so they do not break local-only CI runs.

Catches the chain-of-trust loop-variable shadowing bug that crashed
`_ssl.Certificate` lookups when an unverified chain was returned.
"""

import socket

import pytest

from app.collectors.tls_collector import _handshake_info


# Domains with reliable TLS endpoints. The handshake is short — we just
# need a host that responds to TLS on 443 so the bug path is exercised.
TEST_HOSTS = [
    ("google.com", 443),
    ("cloudflare.com", 443),
]


def _network_reachable() -> bool:
    try:
        socket.gethostbyname("google.com")
        return True
    except OSError:
        return False


@pytest.mark.skipif(
    not _network_reachable(),
    reason="network/DNS unreachable — TLS live tests skipped",
)
@pytest.mark.parametrize("host,port", TEST_HOSTS)
def test_handshake_info_chain_issuers_uses_certificate_attribute(host, port):
    """Regression: chain comprehension must use the Certificate object's
    `issuer` attribute, not shadow the outer `cert` dict and call `.get`.

    The previous code did:
        chain = [cert.get("issuer") for cert in ssock._sslobj.get_unverified_chain()]
    which raised AttributeError on the first iteration of the chain
    because `_ssl.Certificate` objects have no `.get` method.
    """
    result = _handshake_info(host, port)
    assert "error" not in result, f"handshake failed: {result.get('error')}"
    assert "chain_issuers" in result
    # The field is present and the call did not raise. Whether the chain
    # is empty (some hosts return empty unverified chains) or populated,
    # the result must be a list.
    assert isinstance(result["chain_issuers"], list)


@pytest.mark.skipif(
    not _network_reachable(),
    reason="network/DNS unreachable — TLS live tests skipped",
)
@pytest.mark.parametrize("host,port", TEST_HOSTS)
def test_handshake_info_returns_expected_keys(host, port):
    """Sanity: a successful handshake returns the documented fields."""
    result = _handshake_info(host, port)
    assert "error" not in result
    for key in (
        "negotiated_version",
        "cipher",
        "subject",
        "issuer",
        "not_after",
        "expires_at",
        "subject_alt_names",
        "chain_issuers",
        "cert_binary_present",
    ):
        assert key in result, f"missing key {key!r} in handshake result"
