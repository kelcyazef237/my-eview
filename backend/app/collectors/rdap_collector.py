"""RDAP fallback for TLDs not supported by python-whois.

python-whois has no parser for `.int`, `.gov`, `.mil`, and a handful of
other RDAP-only TLDs. When a target domain is on one of those TLDs the
WHOIS collector returns empty fields, which the normalizer marks
NOT_OBSERVED. RDAP (Registration Data Access Protocol) is the modern
replacement and is the authoritative source for those TLDs.

We call `rdap.org` (IANA's bootstrap redirector) which forwards to the
right registry's RDAP server based on the TLD. No new dependencies —
httpx is already in use.
"""

from app.collectors.base import get_bound_httpx_client, with_retry


def _extract_registrar(entities: list[dict]) -> str | None:
    """Pull a friendly name out of the vCardArray for any entity with the
    'registrar' role. RDAP vCard format is a list of [field, params, type,
    value] tuples; we want the `fn` (formatted name) field.
    """
    for entity in entities:
        roles = entity.get("roles") or []
        if "registrar" not in roles:
            continue
        vcard = entity.get("vcardArray")
        if not vcard or len(vcard) < 2 or not vcard[1]:
            continue
        for entry in vcard[1]:
            if entry and entry[0] == "fn" and len(entry) >= 4:
                return entry[3]
    return None


async def collect(domain: str) -> dict:
    """Return RDAP-derived creation_date, expiration_date, registrar.

    Shape mirrors `_whois_raw` so the whois_collector can swap one for
    the other when python-whois returns no dates.
    """

    async def _run() -> dict:
        url = f"https://rdap.org/domain/{domain}"
        async with get_bound_httpx_client(timeout=10, follow_redirects=True) as client:
            r = await client.get(url, headers={"Accept": "application/rdap+json"})
            r.raise_for_status()
            data = r.json()

        events = {
            e.get("eventAction"): e.get("eventDate")
            for e in (data.get("events") or [])
            if e.get("eventAction")
        }
        return {
            "domain": domain,
            "creation_date": events.get("registration"),
            "expiration_date": events.get("expiration"),
            "registrar": _extract_registrar(data.get("entities") or []),
            "name_servers": None,  # RDAP nameservers use a different shape; not used downstream
            "source": "rdap",
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {
            "domain": domain,
            "error": f"{type(error).__name__}: {error}" if error else "unknown failure",
        }
    result["attempts"] = attempts
    return result
