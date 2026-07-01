"""Tests for the parallel AXFR implementation in dns_collector.

The previous implementation called `dns.zone.from_xfr(dns.query.xfr(...))`
serially in a sync function, so a domain with 4 NSes would take up to
120s (4 * lifetime=30). The new implementation runs all NS probes
concurrently with asyncio.gather and reduces `lifetime` to 15s.
"""

import asyncio
import socket
import time
from unittest.mock import patch

import pytest

from app.collectors import dns_collector


def _network_reachable() -> bool:
    try:
        socket.gethostbyname("google.com")
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Pure-logic tests (no network)
# ---------------------------------------------------------------------------

def test_probe_one_ns_returns_ip_on_allow():
    """When dns.zone.from_xfr succeeds, _probe_one_ns returns the IP."""
    fake_zone = object()
    fake_xfr = object()

    captured = {}

    def fake_xfr_factory(*args, **kwargs):
        captured["kwargs"] = kwargs
        return fake_xfr

    with patch.object(dns_collector.dns.zone, "from_xfr", return_value=fake_zone), \
         patch.object(dns_collector.dns.query, "xfr", side_effect=fake_xfr_factory):
        result = dns_collector._probe_one_ns("1.2.3.4", "example.com")
    assert result == "1.2.3.4"
    # Verify lifetime is the new 15s (not 30)
    assert captured["kwargs"].get("lifetime") == 15


def test_probe_one_ns_returns_none_on_refused():
    """When dns.zone.from_xfr raises, _probe_one_ns returns None."""
    with patch.object(dns_collector.dns.zone, "from_xfr", side_effect=Exception("REFUSED")):
        result = dns_collector._probe_one_ns("1.2.3.4", "example.com")
    assert result is None


def test_zone_transfer_status_empty_when_no_nameservers():
    """A domain with no NS records returns tested=0."""
    with patch.object(dns_collector, "_authoritative_nameservers", return_value=[]):
        result = asyncio.run(dns_collector._zone_transfer_status("example.com"))
    assert result == {"tested": 0, "allowed": [], "refused": []}


def test_zone_transfer_status_marks_unresolved_ns_as_refused():
    """If an NS hostname doesn't resolve, it appears in `refused`."""
    with patch.object(
        dns_collector, "_authoritative_nameservers", return_value=["ns1.example.com", "ns2.example.com"]
    ), patch.object(
        dns_collector, "_resolve_ns_ip", side_effect=[None, None]
    ):
        result = asyncio.run(dns_collector._zone_transfer_status("example.com"))
    assert result["tested"] == 2
    assert result["allowed"] == []
    assert sorted(result["refused"]) == ["ns1.example.com", "ns2.example.com"]


def test_zone_transfer_status_marks_allowed_and_refused():
    """A mix of allowed and refused nameservers is reported correctly."""
    with patch.object(
        dns_collector, "_authoritative_nameservers", return_value=["ns1.example.com", "ns2.example.com"]
    ), patch.object(
        dns_collector, "_resolve_ns_ip", side_effect=["1.1.1.1", "2.2.2.2"]
    ), patch.object(
        dns_collector, "_probe_one_ns", side_effect=["1.1.1.1", None]
    ):
        result = asyncio.run(dns_collector._zone_transfer_status("example.com"))
    assert result["tested"] == 2
    assert result["allowed"] == ["ns1.example.com"]
    assert result["refused"] == ["ns2.example.com"]


def test_zone_transfer_status_runs_probes_in_parallel():
    """The probes must be concurrent, not serial. We verify by measuring
    wall-clock time with mocked probes that sleep 0.5s each.
    """
    import time as _time

    def slow_probe(ip, domain):
        _time.sleep(0.5)
        return None

    with patch.object(
        dns_collector, "_authoritative_nameservers", return_value=["ns1.example.com", "ns2.example.com", "ns3.example.com"]
    ), patch.object(
        dns_collector, "_resolve_ns_ip", side_effect=["1.1.1.1", "2.2.2.2", "3.3.3.3"]
    ), patch.object(
        dns_collector, "_probe_one_ns", side_effect=slow_probe
    ):
        t0 = time.perf_counter()
        result = asyncio.run(dns_collector._zone_transfer_status("example.com"))
        elapsed = time.perf_counter() - t0

    # 3 serial probes would take ~1.5s. Parallel should take ~0.5s + overhead.
    # We allow 0.4s slop for thread-pool startup.
    assert result["tested"] == 3
    assert elapsed < 1.0, f"probes appear to be serial (elapsed={elapsed:.2f}s)"


# ---------------------------------------------------------------------------
# Live network test (skipped when DNS is unreachable)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not _network_reachable(),
    reason="network/DNS unreachable — AXFR live test skipped",
)
def test_zone_transfer_status_live_against_google():
    """Smoke test: against a real domain with multiple NSes, the function
    completes and returns a well-formed dict. We don't assert allow/refuse
    because that's server-policy dependent.
    """
    t0 = time.perf_counter()
    result = asyncio.run(dns_collector._zone_transfer_status("google.com"))
    elapsed = time.perf_counter() - t0

    assert "tested" in result
    assert "allowed" in result
    assert "refused" in result
    assert isinstance(result["allowed"], list)
    assert isinstance(result["refused"], list)
    # google.com typically has 4 NSes; the function should test all of them.
    assert result["tested"] >= 2
    # With parallelization, even 4 NSes should complete in well under 20s.
    # (Previously was up to 120s.)
    assert elapsed < 20.0, f"AXFR took too long: {elapsed:.2f}s (serial regression?)"
