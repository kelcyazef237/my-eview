from datetime import datetime, timezone

from app.constants import VectorState


def _f(state: VectorState, meta: dict | None = None) -> dict:
    return {"state": state.value, "meta": meta or {}}


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def normalize_tls(evidence: dict, as_of: datetime | None = None) -> dict:
    if as_of is None:
        as_of = datetime.now(timezone.utc)

    if "error" in evidence:
        return {
            "tls_version": _f(VectorState.NOT_OBSERVED),
            "certificate_health": _f(VectorState.NOT_OBSERVED),
        }

    negotiated = evidence.get("negotiated_version")
    if negotiated == "TLSv1.3":
        tls_state = VectorState.PASS
    elif negotiated == "TLSv1.2":
        tls_state = VectorState.WARN
    elif negotiated in ("TLSv1.1", "TLSv1.0", "SSLv3", "SSLv2"):
        tls_state = VectorState.FAIL
    else:
        tls_state = VectorState.NOT_OBSERVED

    expires_at = _parse_date(evidence.get("expires_at"))
    trusted = evidence.get("cert_trusted", False)

    if expires_at is None:
        cert_state = VectorState.NOT_OBSERVED
    elif not trusted:
        cert_state = VectorState.FAIL
    else:
        remaining_days = (expires_at - as_of).days
        if remaining_days > 90:
            cert_state = VectorState.PASS
        elif remaining_days >= 30:
            cert_state = VectorState.WARN
        else:
            cert_state = VectorState.FAIL

    return {
        "tls_version": _f(tls_state, {"negotiated_version": negotiated}),
        "certificate_health": _f(cert_state, {"remaining_days": remaining_days if expires_at else None}),
    }
