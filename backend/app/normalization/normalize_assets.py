"""Convert asset-discovery evidence into Asset Visibility findings."""

from app.constants import VectorState


def _f(state: VectorState, meta: dict | None = None) -> dict:
    return {"state": state.value, "meta": meta or {}}


COMMON_PREFIXES = {
    "www", "mail", "web", "portal", "api", "app", "secure", "m", "blog",
    "shop", "careers", "investor", "support", "help", "docs", "cdn",
}


def _is_shadow(subdomain: str, primary: str) -> bool:
    prefix = subdomain.replace(f".{primary}", "").split(".")[0].lower()
    return prefix not in COMMON_PREFIXES


def normalize_asset_surface(
    discovery: dict,
    primary_tls: dict | None = None,
    primary_http: dict | None = None,
    subdomain_results: list[dict] | None = None,
) -> dict:
    """Return findings for asset_count, shadow_assets, and unmanaged_assets."""
    if "error" in discovery:
        return {
            "asset_count": _f(VectorState.NOT_OBSERVED),
            "shadow_assets": _f(VectorState.NOT_OBSERVED),
            "unmanaged_assets": _f(VectorState.NOT_OBSERVED),
        }

    assets = discovery.get("discovered_assets") or []
    domain = discovery.get("domain", "")
    count = len(assets)

    if count <= 10:
        count_state = VectorState.PASS
    elif count <= 30:
        count_state = VectorState.WARN
    else:
        count_state = VectorState.FAIL

    if not assets:
        return {
            "asset_count": _f(count_state, {"count": count}),
            "shadow_assets": _f(VectorState.NOT_APPLICABLE),
            "unmanaged_assets": _f(VectorState.NOT_APPLICABLE),
        }

    shadow_count = sum(1 for a in assets if _is_shadow(a, domain))
    if shadow_count == 0:
        shadow_state = VectorState.PASS
    elif shadow_count <= 2 or (shadow_count / count) <= 0.10:
        shadow_state = VectorState.PASS
    elif shadow_count <= 5 or (shadow_count / count) <= 0.25:
        shadow_state = VectorState.WARN
    else:
        shadow_state = VectorState.FAIL

    primary_issuer = None
    if primary_tls:
        primary_issuer = primary_tls.get("issuer")

    indicators = 0
    expired_or_untrusted = 0
    probes_attempted = 0
    probes_failed = 0
    for sub in subdomain_results or []:
        probes_attempted += 1
        sub_tls = sub.get("tls") or {}
        sub_http = sub.get("http") or {}
        if "error" in sub_tls or "error" in sub_http:
            probes_failed += 1
            continue
        if not sub_tls.get("cert_trusted"):
            expired_or_untrusted += 1
        if primary_issuer and sub_tls.get("issuer") and sub_tls.get("issuer") != primary_issuer:
            indicators += 1
        sub_server = (sub_http.get("https_root") or {}).get("tech_headers", {}).get("server")
        primary_server = (primary_http or {}).get("https_root", {}).get("tech_headers", {}).get("server") if primary_http else None
        if sub_server and primary_server and sub_server != primary_server:
            indicators += 1

    if expired_or_untrusted >= 1 or indicators >= 3:
        unmanaged_state = VectorState.FAIL
    elif indicators >= 1:
        unmanaged_state = VectorState.WARN
    else:
        unmanaged_state = VectorState.PASS

    # Data-loss guard: if we attempted many probes and most failed, the
    # "PASS" outcome above is driven by silence, not by evidence. Escalate
    # to WARN so the user sees that we couldn't tell, not that everything
    # was clean. Threshold chosen so a single 1-of-1 failure does not
    # trip this — we only escalate when the failure pattern is genuine.
    # We do NOT downgrade a real FAIL to WARN — the data-loss guard only
    # escalates a PASS to WARN.
    if probes_attempted >= 5 and probes_failed / probes_attempted > 0.5:
        if unmanaged_state == VectorState.PASS:
            unmanaged_state = VectorState.WARN

    return {
        "asset_count": _f(count_state, {"count": count}),
        "shadow_assets": _f(shadow_state, {"shadow_count": shadow_count, "total": count}),
        "unmanaged_assets": _f(
            unmanaged_state,
            {
                "indicators": indicators,
                "expired_or_untrusted": expired_or_untrusted,
                "probes_attempted": probes_attempted,
                "probes_failed": probes_failed,
            },
        ),
    }
