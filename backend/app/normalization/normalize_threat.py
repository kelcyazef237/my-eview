from app.constants import VectorState


def _f(state: VectorState, meta: dict | None = None) -> dict:
    return {"state": state.value, "meta": meta or {}}


def normalize_threat(evidence: dict) -> dict:
    if "error" in evidence:
        return {
            "malware": _f(VectorState.NOT_OBSERVED),
            "phishing": _f(VectorState.NOT_OBSERVED),
            "spam_blacklist": _f(VectorState.NOT_OBSERVED),
            "botnet": _f(VectorState.NOT_OBSERVED),
            "blacklist_aggregate": _f(VectorState.NOT_OBSERVED),
        }

    derived = evidence.get("derived", {})

    def _activity_state(activity: str) -> dict:
        if activity == "active":
            return _f(VectorState.FAIL, {"activity": "active"})
        if activity == "historical":
            return _f(VectorState.WARN, {"activity": "historical"})
        return _f(VectorState.PASS, {"activity": "none"})

    malware_state = _activity_state(derived.get("malware_activity", "none"))
    phishing_state = _activity_state(derived.get("phishing_activity", "none"))

    botnet_listed = derived.get("botnet_listed", False)
    if botnet_listed:
        botnet_state = _f(VectorState.FAIL, {"activity": "active"})
    else:
        botnet_state = _f(VectorState.PASS, {"activity": "none"})

    spam_count = derived.get("spam_listed_count", 0)
    if spam_count == 0:
        spam_state = _f(VectorState.PASS)
    elif spam_count == 1:
        spam_state = _f(VectorState.WARN, {"listed_count": spam_count})
    else:
        spam_state = _f(VectorState.FAIL, {"listed_count": spam_count})

    aggregate = derived.get("blacklist_aggregate_count", 0)
    if aggregate <= 1:
        aggregate_state = _f(VectorState.PASS)
    elif aggregate <= 3:
        aggregate_state = _f(VectorState.WARN, {"count": aggregate})
    else:
        aggregate_state = _f(VectorState.FAIL, {"count": aggregate})

    return {
        "malware": malware_state,
        "phishing": phishing_state,
        "spam_blacklist": spam_state,
        "botnet": botnet_state,
        "blacklist_aggregate": aggregate_state,
    }
