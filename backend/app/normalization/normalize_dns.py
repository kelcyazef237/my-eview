from datetime import datetime, timezone

from app.constants import VectorState


def _f(state: VectorState, meta: dict | None = None) -> dict:
    return {"state": state.value, "meta": meta or {}}


def normalize_dns(evidence: dict) -> dict:
    """Convert DNS raw evidence into scoring-engine findings."""
    if "error" in evidence:
        return {
            "spf_presence": _f(VectorState.NOT_OBSERVED),
            "dkim_presence": _f(VectorState.NOT_OBSERVED),
            "dmarc_enforcement": _f(VectorState.NOT_OBSERVED),
            "dnssec_adoption": _f(VectorState.NOT_OBSERVED),
            "zone_transfer": _f(VectorState.NOT_OBSERVED),
        }

    spf = VectorState.PASS if evidence.get("spf_present") else VectorState.FAIL
    dkim = VectorState.PASS if evidence.get("dkim_present") else VectorState.FAIL

    dmarc_policy = evidence.get("dmarc_policy", "absent")
    if dmarc_policy == "reject":
        dmarc = VectorState.PASS
    elif dmarc_policy == "quarantine":
        dmarc = VectorState.WARN
    elif dmarc_policy == "none":
        dmarc = VectorState.WARN
    else:
        dmarc = VectorState.FAIL

    dnssec = evidence.get("dnssec", {})
    ds = dnssec.get("ds", False)
    dnskey = dnssec.get("dnskey", False)
    rrsig = dnssec.get("rrsig", False)
    if ds and dnskey:
        dnssec_state = VectorState.PASS
    elif ds or dnskey or rrsig:
        dnssec_state = VectorState.WARN
    else:
        dnssec_state = VectorState.FAIL

    zone_transfer = evidence.get("zone_transfer", {})
    allowed_ns = zone_transfer.get("allowed", [])
    if zone_transfer.get("tested", 0) == 0:
        zt_state = VectorState.NOT_OBSERVED
    elif allowed_ns:
        zt_state = VectorState.FAIL
    else:
        zt_state = VectorState.PASS

    return {
        "spf_presence": _f(spf),
        "dkim_presence": _f(dkim),
        "dmarc_enforcement": _f(dmarc, {"dmarc_policy": dmarc_policy}),
        "dnssec_adoption": _f(dnssec_state),
        "zone_transfer": _f(zt_state, {
            "nameservers_tested": zone_transfer.get("tested", 0),
            "allowed_nameservers": allowed_ns,
        }),
    }
