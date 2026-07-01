"""Tests for the parallel subdomain probe in scan_orchestrator.

The previous implementation ran 20 subdomain probes serially in a
`for sub in discovered[:20]:` loop, taking ~160s on a 20-subdomain target
(each subdomain does a TLS+HTTP gather at ~8s). The new implementation
fans out the probes with `asyncio.gather` + `asyncio.Semaphore(5)`,
completing 20 subdomains in ~4 batches instead of 20 serial rounds.

These tests exercise the extracted `_probe_subdomains` helper directly,
without the full DB / schema / orchestrator setup. The helper is the
part that implements the parallelism; the orchestrator is glue around
it.
"""

import asyncio
import time
from unittest.mock import AsyncMock

from app.services.scan_orchestrator import (
    SUBDOMAIN_CONCURRENCY,
    _probe_subdomains,
)


# ---------------------------------------------------------------------------
# Parallelism invariant
# ---------------------------------------------------------------------------

def test_probe_subdomains_runs_in_parallel():
    """20 subdomains with a 1s per-probe delay should finish in ~4-5s,
    not 20s. The semaphore caps concurrency at SUBDOMAIN_CONCURRENCY=5,
    so 20 subdomains complete in ceil(20/5)=4 batches.
    """
    sub_count = 20
    per_probe_delay = 1.0

    async def slow_tls(sub):
        await asyncio.sleep(per_probe_delay)
        return {"host": sub, "negotiated_version": "TLSv1.3"}

    async def slow_http(sub):
        await asyncio.sleep(per_probe_delay)
        return {"domain": sub, "https_root": {"status_code": 200}}

    fake_tls = AsyncMock()
    fake_http = AsyncMock()
    fake_tls.collect = slow_tls
    fake_http.collect = slow_http

    t0 = time.perf_counter()
    results = asyncio.run(
        _probe_subdomains(
            [f"sub{i}.example.com" for i in range(sub_count)],
            fake_tls, fake_http,
        )
    )
    elapsed = time.perf_counter() - t0

    # All subdomains probed.
    assert len(results) == sub_count
    # Serial would take ~20s. With 5x parallelism, expect ~4-6s + scheduling overhead.
    assert elapsed < 10.0, (
        f"Subdomain probes appear serial: elapsed={elapsed:.2f}s "
        f"(serial would be {sub_count * per_probe_delay:.0f}s)"
    )


def test_probe_subdomains_caps_concurrency_at_semaphore():
    """The semaphore caps the number of *outer* subdomain probes running
    at the same time. Each outer probe fans out to TLS+HTTP in parallel
    inside the semaphore, so the true peak of in-flight network
    operations is `SUBDOMAIN_CONCURRENCY * 2` (one TLS + one HTTP per
    probe). This is still well within "polite scanner" territory.
    """
    # We use the same slow_inner for both TLS and HTTP. The outer
    # counter is incremented by wrapping the gather in `slow_outer`.
    inner_in_flight = 0
    inner_peak = 0
    inner_lock = asyncio.Lock()

    async def slow_inner(label):
        nonlocal inner_in_flight, inner_peak
        async with inner_lock:
            inner_in_flight += 1
            inner_peak = max(inner_peak, inner_in_flight)
        try:
            await asyncio.sleep(0.3)
            return {"host": label}
        finally:
            async with inner_lock:
                inner_in_flight -= 1

    # `fake_tls.collect` / `fake_http.collect` mirror the real signature
    # of the corresponding modules. The helper calls them in parallel
    # inside one semaphore slot, so each call to `slow_inner` represents
    # ONE network operation (TLS or HTTP).
    fake_tls = AsyncMock()
    fake_http = AsyncMock()
    fake_tls.collect = slow_inner
    fake_http.collect = slow_inner

    asyncio.run(
        _probe_subdomains(
            [f"sub{i}.example.com" for i in range(15)],
            fake_tls, fake_http,
        )
    )

    # 15 subdomains / cap 5 = 3 batches. Each batch runs 5 outer
    # probes in parallel, each with TLS+HTTP inside = 10 inner network
    # calls in flight at peak.
    assert inner_peak == SUBDOMAIN_CONCURRENCY * 2, (
        f"Expected exactly {SUBDOMAIN_CONCURRENCY * 2} inner calls in flight "
        f"(5 outer probes × TLS+HTTP fanout), saw peak={inner_peak}"
    )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_probe_subdomains_empty_list_returns_empty():
    """Zero subdomains → empty result, no errors."""
    fake_tls = AsyncMock()
    fake_http = AsyncMock()
    results = asyncio.run(_probe_subdomains([], fake_tls, fake_http))
    assert results == []


def test_probe_subdomains_handles_collector_exceptions():
    """If a probe raises, that subdomain's result carries an error dict
    (other subdomains still complete). The orchestrator's unwrap logic
    relies on this — if it changes, normalize_assets and the diagnostic
    both break.
    """
    async def failing_tls(sub):
        raise ConnectionError(f"tls boom for {sub}")

    async def ok_http(sub):
        return {"domain": sub, "https_root": {"status_code": 200}}

    fake_tls = AsyncMock()
    fake_http = AsyncMock()
    fake_tls.collect = failing_tls
    fake_http.collect = ok_http

    results = asyncio.run(
        _probe_subdomains(
            ["sub1.example.com", "sub2.example.com"],
            fake_tls, fake_http,
        )
    )
    assert len(results) == 2
    for r in results:
        assert "error" in r["tls"], (
            f"tls collector exception should be unwrapped into error dict, "
            f"got: {r['tls']!r}"
        )
        # HTTP was ok so no error key there.
        assert r["http"]["https_root"]["status_code"] == 200
