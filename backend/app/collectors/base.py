"""Shared collector infrastructure: retry, source-IP binding, 2-of-3 agreement."""

import asyncio
import functools
from collections import Counter
from typing import Any, Callable, Coroutine, TypeVar

import httpx

from app.config import get_settings

T = TypeVar("T")

settings = get_settings()


def _source_address_tuple() -> tuple[str | None, int] | None:
    """Return (source_ip, 0) if a specific bind address is configured, else None."""
    bind = settings.collector_bind_address
    if bind and bind not in ("0.0.0.0", "::", ""):
        return (bind, 0)
    return None


def get_bound_httpx_client(**kwargs) -> httpx.AsyncClient:
    """Return an httpx.AsyncClient bound to COLLECTOR_BIND_ADDRESS when set."""
    source = _source_address_tuple()
    if source:
        transport = httpx.AsyncHTTPTransport(local_address=source[0])
        kwargs.setdefault("transport", transport)
    return httpx.AsyncClient(**kwargs)


async def with_retry(
    coro_fn: Callable[[], Coroutine[Any, Any, T]],
    max_attempts: int | None = None,
    backoff_seconds: float | None = None,
) -> tuple[T | None, int, Exception | None]:
    """Run an async coroutine with exponential backoff.

    Returns a tuple of (result, attempt_count, final_error). On success final_error
    is None and result is the returned value. On failure result is None and
    final_error is the last exception encountered.
    """
    max_attempts = max_attempts or settings.collector_max_retries
    backoff = backoff_seconds or settings.collector_retry_backoff_seconds
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await coro_fn(), attempt, None
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt < max_attempts:
                await asyncio.sleep(backoff * (2 ** (attempt - 1)))
    return None, max_attempts, last_error


async def require_agreement(
    coro_fn: Callable[[], Coroutine[Any, Any, str]],
    attempts: int = 3,
    threshold: int = 2,
) -> tuple[str, int, Exception | None]:
    """Run a flaky collector multiple times and require >=threshold matching states.

    Returns (state, count_run, final_error). If no state reaches the threshold,
    returns (NOT_OBSERVED, count_run, None).
    """
    results: list[str] = []
    last_error: Exception | None = None
    for i in range(attempts):
        try:
            state = await coro_fn()
            results.append(state)
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    if results:
        most_common, count = Counter(results).most_common(1)[0]
        if count >= threshold:
            return most_common, len(results), last_error

    return "NOT_OBSERVED", len(results), last_error


def run_in_thread(func: Callable[..., T], *args, **kwargs) -> Coroutine[Any, Any, T]:
    """Wrap a synchronous blocking function in asyncio.to_thread."""
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
