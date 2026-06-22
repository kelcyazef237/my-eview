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


def normalize_whois(evidence: dict, as_of: datetime | None = None) -> dict:
    if as_of is None:
        as_of = datetime.now(timezone.utc)

    if "error" in evidence:
        return {
            "domain_age": _f(VectorState.NOT_OBSERVED),
            "domain_expiration": _f(VectorState.NOT_OBSERVED),
        }

    created = _parse_date(evidence.get("creation_date"))
    expires = _parse_date(evidence.get("expiration_date"))

    if created:
        age_days = (as_of - created).days
        if age_days > 365:
            age_state = VectorState.PASS
        elif age_days >= 180:
            age_state = VectorState.WARN
        else:
            age_state = VectorState.FAIL
    else:
        age_state = VectorState.NOT_OBSERVED

    if expires:
        remaining_days = (expires - as_of).days
        if remaining_days > 90:
            expiration_state = VectorState.PASS
        elif remaining_days >= 30:
            expiration_state = VectorState.WARN
        else:
            expiration_state = VectorState.FAIL
    else:
        expiration_state = VectorState.NOT_OBSERVED

    return {
        "domain_age": _f(age_state),
        "domain_expiration": _f(expiration_state),
    }
