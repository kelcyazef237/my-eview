"""Regression test for the diag_scan axfr probe regression.

After the AXFR parallelization (commit 6d827c5), `_zone_transfer_status`
became async. The diag script at probe_axfr was wrapping it in
`asyncio.to_thread` — which returns a coroutine object, not a result
dict. Calling `.get()` on a coroutine raised AttributeError.

The fix: just `await` the function directly.

This test imports the probe and exercises it against a real domain
(network-skip when unreachable).
"""

import asyncio
import socket
import sys
from pathlib import Path

import pytest

# Make sure backend/scripts is on the path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = BACKEND_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


def _network_reachable() -> bool:
    try:
        socket.gethostbyname("google.com")
        return True
    except OSError:
        return False


@pytest.mark.skipif(
    not _network_reachable(),
    reason="network/DNS unreachable — diag live test skipped",
)
def test_probe_axfr_does_not_call_coroutine_get():
    """The regression: probe_axfr returned AttributeError because
    `await asyncio.to_thread(_zone_transfer_status, ...)` gives a
    coroutine, not a dict. This test runs the probe against google.com
    and asserts no AttributeError and a well-formed result.
    """
    # Import here so the scripts-dir insertion above happens first.
    from diag_scan import probe_axfr

    # Build a minimal logger mock. The probe uses logger.emit("STAGE", ...),
    # logger.emit("PASS", ...), logger.emit("FAIL", ...), logger.emit("WARN", ...).
    class _StubLogger:
        def __init__(self):
            self.events = []

        def emit(self, tag: str, msg: str) -> None:
            self.events.append((tag, msg))

    # The probe takes (logger, domain). The actual logger argument is
    # typed as DiagLogger but in practice any object with .emit works.
    logger = _StubLogger()
    result = asyncio.run(probe_axfr(logger, "google.com"))

    # Either we got a result dict or None on hard failure — but it
    # must NOT be a coroutine object.
    assert result is None or isinstance(result, dict), (
        f"probe_axfr returned {type(result).__name__}, expected dict or None"
    )

    # No FAIL event should have been emitted with the coroutine error.
    fail_events = [msg for tag, msg in logger.events if tag == "FAIL"]
    for msg in fail_events:
        assert "coroutine" not in msg, (
            f"probe_axfr hit the regression — coroutine.get() in log: {msg}"
        )
