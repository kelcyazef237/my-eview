"""Tests for the RDAP collector and its fallback integration in whois_collector.

python-whois has no parser for `.int`, `.gov`, `.mil`, and a handful of
other RDAP-only TLDs. The RDAP collector provides a fallback so those
domains can still produce `creation_date` and `expiration_date` instead
of silently going NOT_OBSERVED.
"""

import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.collectors import rdap_collector, whois_collector


def _network_reachable() -> bool:
    try:
        socket.gethostbyname("rdap.org")
        return True
    except OSError:
        return False


# ---------------------------------------------------------------------------
# vCard extraction
# ---------------------------------------------------------------------------

def test_extract_registrar_finds_fn_in_registrar_entity():
    """The registrar role's vCardArray[1] contains an `fn` field we want."""
    entities = [
        {"roles": ["registrar"], "vcardArray": [
            "vcard",
            [["version", {}, "text", "4.0"],
             ["fn", {}, "text", "Example Registrar Inc."]],
        ]},
    ]
    assert rdap_collector._extract_registrar(entities) == "Example Registrar Inc."


def test_extract_registrar_skips_non_registrar_entities():
    """An entity with no 'registrar' role is ignored."""
    entities = [
        {"roles": ["abuse"], "vcardArray": [
            "vcard",
            [["fn", {}, "text", "Abuse Contact"]],
        ]},
    ]
    assert rdap_collector._extract_registrar(entities) is None


def test_extract_registrar_handles_missing_vcard():
    """Entities with no vcardArray don't crash and return None."""
    entities = [{"roles": ["registrar"]}]
    assert rdap_collector._extract_registrar(entities) is None


def test_extract_registrar_handles_empty_entity_list():
    assert rdap_collector._extract_registrar([]) is None


# ---------------------------------------------------------------------------
# Collect — mocked HTTP
# ---------------------------------------------------------------------------

def _mock_rdap_response(events=None, entities=None):
    """Build a mock httpx.Response that returns the given RDAP JSON."""
    response = MagicMock()
    response.json.return_value = {
        "events": events or [],
        "entities": entities or [],
    }
    response.raise_for_status = MagicMock()
    return response


def test_collect_parses_events_and_registrar():
    """The happy path: events carry registration/expiration, entities carry registrar."""
    response = _mock_rdap_response(
        events=[
            {"eventAction": "registration", "eventDate": "2000-01-01T00:00:00Z"},
            {"eventAction": "expiration", "eventDate": "2030-01-01T00:00:00Z"},
        ],
        entities=[
            {"roles": ["registrar"], "vcardArray": [
                "vcard",
                [["fn", {}, "text", "ICANN Test Registrar"]],
            ]},
        ],
    )

    # Patch the AsyncClient context manager.
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.get = AsyncMock(return_value=response)

    with patch.object(rdap_collector, "get_bound_httpx_client", return_value=client):
        result = asyncio_run(rdap_collector.collect("beac.int"))

    assert result["creation_date"] == "2000-01-01T00:00:00Z"
    assert result["expiration_date"] == "2030-01-01T00:00:00Z"
    assert result["registrar"] == "ICANN Test Registrar"
    assert result["source"] == "rdap"
    assert "error" not in result


def test_collect_returns_error_on_http_failure():
    """If rdap.org returns a non-2xx, the result carries a typed error."""
    from httpx import HTTPStatusError

    response = MagicMock()
    response.raise_for_status.side_effect = HTTPStatusError("404", request=MagicMock(), response=MagicMock())

    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.get = AsyncMock(return_value=response)

    with patch.object(rdap_collector, "get_bound_httpx_client", return_value=client):
        result = asyncio_run(rdap_collector.collect("nonexistent.invalid"))

    assert "error" in result
    assert "HTTPStatusError" in result["error"]


# ---------------------------------------------------------------------------
# WHOIS→RDAP fallback integration
# ---------------------------------------------------------------------------

def test_whois_uses_rdap_when_whois_returns_no_dates():
    """If python-whois returns empty fields (e.g. for .int), RDAP is tried."""
    empty_whois = {
        "domain": "beac.int",
        "creation_date": None,
        "expiration_date": None,
        "registrar": None,
        "name_servers": None,
    }
    rdap_filled = {
        "domain": "beac.int",
        "creation_date": "2003-06-26T00:00:00Z",
        "expiration_date": "2026-06-26T00:00:00Z",
        "registrar": "Some Registrar",
        "name_servers": None,
        "source": "rdap",
    }

    with patch.object(whois_collector, "_whois_raw", return_value=empty_whois), \
         patch.object(whois_collector, "rdap_collect", new=AsyncMock(return_value=rdap_filled)) as mock_rdap:
        result = asyncio_run(whois_collector.collect("beac.int"))

    mock_rdap.assert_awaited_once_with("beac.int")
    assert result["creation_date"] == "2003-06-26T00:00:00Z"
    assert result["source"] == "rdap"


def test_whois_skips_rdap_when_whois_succeeds():
    """When python-whois returns dates, RDAP is NOT called."""
    whois_filled = {
        "domain": "example.com",
        "creation_date": "2000-01-01T00:00:00Z",
        "expiration_date": "2030-01-01T00:00:00Z",
        "registrar": "Some Registrar",
        "name_servers": None,
    }

    with patch.object(whois_collector, "_whois_raw", return_value=whois_filled), \
         patch.object(whois_collector, "rdap_collect", new=AsyncMock()) as mock_rdap:
        result = asyncio_run(whois_collector.collect("example.com"))

    mock_rdap.assert_not_called()
    assert result["creation_date"] == "2000-01-01T00:00:00Z"


def test_whois_returns_whois_result_when_rdap_also_empty():
    """If RDAP returns no dates either, return the original empty WHOIS result
    so the normalizer marks it NOT_OBSERVED (and doesn't claim RDAP coverage
    falsely)."""
    empty_whois = {
        "domain": "beac.int",
        "creation_date": None,
        "expiration_date": None,
        "registrar": None,
        "name_servers": None,
    }
    rdap_also_empty = {
        "domain": "beac.int",
        "creation_date": None,
        "expiration_date": None,
        "registrar": None,
        "name_servers": None,
        "source": "rdap",
    }

    with patch.object(whois_collector, "_whois_raw", return_value=empty_whois), \
         patch.object(whois_collector, "rdap_collect", new=AsyncMock(return_value=rdap_also_empty)):
        result = asyncio_run(whois_collector.collect("beac.int"))

    # No source stamp: this is the WHOIS pass-through, not the RDAP result.
    assert result.get("source") != "rdap"
    assert result["creation_date"] is None


# ---------------------------------------------------------------------------
# Helper: run a coroutine synchronously in tests
# ---------------------------------------------------------------------------

def asyncio_run(coro):
    """Tiny helper so tests don't need pytest-asyncio."""
    import asyncio
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# Live network smoke test
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not _network_reachable(),
    reason="network/DNS unreachable — RDAP live test skipped",
)
def test_rdap_collect_live_against_int_tld():
    """End-to-end: query rdap.org for a real .int domain and verify shape."""
    result = asyncio_run(rdap_collector.collect("beac.int"))
    # We can't assert dates because beac.int may have been re-registered,
    # but the result must be a well-formed dict with our documented keys.
    assert "domain" in result
    assert "creation_date" in result
    assert "expiration_date" in result
    assert "registrar" in result
    assert "error" not in result, f"unexpected error: {result.get('error')}"
