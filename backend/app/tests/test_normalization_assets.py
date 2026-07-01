"""Regression tests for the data-loss guard in normalize_asset_surface.

The previous implementation silently `continue`d past subdomain entries
whose TLS probe had errored, so a target whose network rejected all
subdomain probes would get a green PASS on `unmanaged_assets` despite
zero observations. The new implementation counts failed probes and
escalates to WARN when most probes failed and we attempted at least 5.
"""

from app.constants import VectorState
from app.normalization.normalize_assets import normalize_asset_surface


def _good_sub():
    """A subdomain probe that produced a clean, trusted cert."""
    return {
        "tls": {"cert_trusted": True, "issuer": "Primary CA"},
        "http": {"https_root": {"tech_headers": {"server": "nginx"}}},
    }


def _errored_sub(err: str = "timeout"):
    """A subdomain probe that failed (TLS or HTTP)."""
    return {"tls": {"error": err}, "http": {"https_root": {"tech_headers": {"server": "nginx"}}}}


def _errored_http_sub(err: str = "ReadTimeout"):
    """A subdomain probe that failed only on HTTP (TLS succeeded)."""
    return {
        "tls": {"cert_trusted": True, "issuer": "Primary CA"},
        "http": {"error": err},
    }


def _discovery(count: int = 5) -> dict:
    """Return a discovery result with N placeholder assets."""
    return {
        "domain": "example.com",
        "discovered_assets": [f"sub{i}.example.com" for i in range(count)],
        "count": count,
    }


def _primary_tls():
    return {"issuer": "Primary CA"}


def _primary_http():
    return {"https_root": {"tech_headers": {"server": "nginx"}}}


def test_unmanaged_assets_pass_when_all_subdomains_clean():
    """Happy path: all subdomain probes succeed, all match primary — PASS."""
    subs = [_good_sub() for _ in range(5)]
    result = normalize_asset_surface(
        _discovery(5), _primary_tls(), _primary_http(), subs
    )
    assert result["unmanaged_assets"]["state"] == VectorState.PASS.value
    meta = result["unmanaged_assets"]["meta"]
    assert meta["probes_attempted"] == 5
    assert meta["probes_failed"] == 0


def test_unmanaged_assets_warn_when_all_subdomains_failed():
    """The bug: all 5 probes failed → should be WARN, not PASS."""
    subs = [_errored_sub() for _ in range(5)]
    result = normalize_asset_surface(
        _discovery(5), _primary_tls(), _primary_http(), subs
    )
    assert result["unmanaged_assets"]["state"] == VectorState.WARN.value
    meta = result["unmanaged_assets"]["meta"]
    assert meta["probes_attempted"] == 5
    assert meta["probes_failed"] == 5
    # Indicators and expired_or_untrusted stay 0 because we couldn't observe them.
    assert meta["indicators"] == 0
    assert meta["expired_or_untrusted"] == 0


def test_unmanaged_assets_warn_when_only_http_fails():
    """The data-loss guard counts both TLS and HTTP errors."""
    subs = [_errored_http_sub() for _ in range(5)]
    result = normalize_asset_surface(
        _discovery(5), _primary_tls(), _primary_http(), subs
    )
    assert result["unmanaged_assets"]["state"] == VectorState.WARN.value
    assert result["unmanaged_assets"]["meta"]["probes_failed"] == 5


def test_unmanaged_assets_pass_when_few_subdomains_and_one_fails():
    """Below the threshold: small N, single failure should not trip the guard."""
    subs = [_good_sub(), _good_sub(), _errored_sub(), _good_sub()]
    result = normalize_asset_surface(
        _discovery(4), _primary_tls(), _primary_http(), subs
    )
    # 4 attempts, 1 failure — guard does not engage (threshold is 5 attempts)
    assert result["unmanaged_assets"]["state"] == VectorState.PASS.value


def test_unmanaged_assets_warn_at_threshold_boundary():
    """5 attempts, 3 failures (>50%) → guard trips."""
    subs = [_good_sub(), _errored_sub(), _errored_sub(), _errored_sub(), _good_sub()]
    result = normalize_asset_surface(
        _discovery(5), _primary_tls(), _primary_http(), subs
    )
    assert result["unmanaged_assets"]["state"] == VectorState.WARN.value
    assert result["unmanaged_assets"]["meta"]["probes_attempted"] == 5
    assert result["unmanaged_assets"]["meta"]["probes_failed"] == 3


def test_unmanaged_assets_pass_at_threshold_boundary_5_of_5_ok():
    """5 attempts, 0 failures → still PASS (not WARN)."""
    subs = [_good_sub() for _ in range(5)]
    result = normalize_asset_surface(
        _discovery(5), _primary_tls(), _primary_http(), subs
    )
    assert result["unmanaged_assets"]["state"] == VectorState.PASS.value


def test_unmanaged_assets_pass_when_failure_ratio_low_but_n_high():
    """10 attempts, 4 failures (40%) → not >50%, guard does not engage."""
    subs = [_good_sub() for _ in range(6)] + [_errored_sub() for _ in range(4)]
    result = normalize_asset_surface(
        _discovery(10), _primary_tls(), _primary_http(), subs
    )
    # 4/10 = 0.4, not > 0.5
    assert result["unmanaged_assets"]["state"] == VectorState.PASS.value


def test_unmanaged_assets_warn_does_not_override_real_fail():
    """If real evidence points to FAIL, the data-loss guard should not downgrade it."""
    # 5 subdomains, 4 errored, 1 with an untrusted cert.
    subs = [
        _errored_sub(), _errored_sub(), _errored_sub(), _errored_sub(),
        {"tls": {"cert_trusted": False, "issuer": "Some CA"},
         "http": {"https_root": {"tech_headers": {"server": "nginx"}}}},
    ]
    result = normalize_asset_surface(
        _discovery(5), _primary_tls(), _primary_http(), subs
    )
    # expired_or_untrusted=1 from the one good observation → FAIL beats WARN escalation.
    assert result["unmanaged_assets"]["state"] == VectorState.FAIL.value
