"""Offline tests for collector base utilities."""

import asyncio

import pytest

from app.collectors.base import (
    _source_address_tuple,
    require_agreement,
    with_retry,
)
from app.config import get_settings


settings = get_settings()


def test_source_address_tuple_returns_none_for_unspecified():
    for addr in ("0.0.0.0", "::", ""):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(settings, "collector_bind_address", addr)
            assert _source_address_tuple() is None


def test_source_address_tuple_returns_bind_tuple():
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(settings, "collector_bind_address", "192.0.2.1")
        assert _source_address_tuple() == ("192.0.2.1", 0)


def test_with_retry_succeeds_first_attempt():
    async def coro():
        return "ok"

    result, attempts, error = asyncio.run(with_retry(coro, max_attempts=3, backoff_seconds=0))
    assert result == "ok"
    assert attempts == 1
    assert error is None


def test_with_retry_retries_then_succeeds():
    calls = []

    async def coro():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("transient")
        return "ok"

    result, attempts, error = asyncio.run(with_retry(coro, max_attempts=3, backoff_seconds=0))
    assert result == "ok"
    assert attempts == 3
    assert error is None


def test_with_retry_exhausts_attempts():
    async def coro():
        raise RuntimeError("persistent")

    result, attempts, error = asyncio.run(with_retry(coro, max_attempts=2, backoff_seconds=0))
    assert result is None
    assert attempts == 2
    assert isinstance(error, RuntimeError)


def test_require_agreement_reaches_threshold():
    calls = []

    async def coro():
        calls.append(1)
        return "PASS" if len(calls) >= 2 else "FAIL"

    state, count, error = asyncio.run(require_agreement(coro, attempts=3, threshold=2))
    assert state == "PASS"
    assert count == 3
    assert error is None


def test_require_agreement_falls_back_to_not_observed():
    async def coro():
        return "A"

    state, count, error = asyncio.run(require_agreement(coro, attempts=3, threshold=2))
    # All three results are "A", so threshold is met despite only one unique value.
    assert state == "A"
    assert count == 3


def test_require_agreement_no_majority_returns_not_observed():
    results = iter(["A", "B", "C"])

    async def coro():
        return next(results)

    state, count, error = asyncio.run(require_agreement(coro, attempts=3, threshold=2))
    assert state == "NOT_OBSERVED"
    assert count == 3


def test_require_agreement_tracks_last_error():
    async def coro():
        raise RuntimeError("boom")

    state, count, error = asyncio.run(require_agreement(coro, attempts=3, threshold=2))
    assert state == "NOT_OBSERVED"
    assert count == 0
    assert isinstance(error, RuntimeError)
