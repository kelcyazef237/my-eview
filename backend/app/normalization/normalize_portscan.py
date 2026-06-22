from app.constants import VectorState


def normalize_legacy_service(evidence: dict) -> dict:
    if "error" in evidence or evidence.get("skipped"):
        return {"state": VectorState.NOT_APPLICABLE.value}

    exposed = evidence.get("exposed_count", 0)
    plaintext = evidence.get("plaintext_count", 0)
    if exposed == 0:
        return {"state": VectorState.PASS.value}
    if plaintext >= 1 or exposed >= 2:
        return {"state": VectorState.FAIL.value, "meta": {"exposed_ports": evidence.get("exposed_ports", [])}}
    return {"state": VectorState.WARN.value, "meta": {"exposed_ports": evidence.get("exposed_ports", [])}}
