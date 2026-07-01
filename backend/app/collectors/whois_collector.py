"""WHOIS/RDAP collector for domain age and expiration."""

import asyncio
from datetime import datetime, timezone

import whois

from app.collectors.base import run_in_thread, with_retry
from app.collectors.rdap_collector import collect as rdap_collect


def _coerce_date(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, list):
        value = value[0]
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    return None


def _whois_raw(domain: str) -> dict:
    try:
        w = whois.whois(domain)
    except Exception as exc:
        return {"domain": domain, "error": str(exc)}

    created = _coerce_date(getattr(w, "creation_date", None))
    expires = _coerce_date(getattr(w, "expiration_date", None))
    registrar = getattr(w, "registrar", None)
    name_servers = getattr(w, "name_servers", None)

    return {
        "domain": domain,
        "creation_date": created.isoformat() if created else None,
        "expiration_date": expires.isoformat() if expires else None,
        "registrar": registrar,
        "name_servers": name_servers,
    }


async def collect(domain: str) -> dict:
    async def _run() -> dict:
        whois_result = await run_in_thread(_whois_raw, domain)
        # python-whois returns empty fields for RDAP-only TLDs (.int, .gov,
        # .mil, and a handful of ccTLDs). When the WHOIS query produced no
        # usable dates, try RDAP before giving up.
        if whois_result.get("creation_date") or whois_result.get("expiration_date"):
            return whois_result
        if "error" in whois_result:
            return whois_result
        rdap_result = await rdap_collect(domain)
        if "error" not in rdap_result and (
            rdap_result.get("creation_date") or rdap_result.get("expiration_date")
        ):
            return rdap_result
        # RDAP also failed — return the original WHOIS result so the
        # normalizer can mark it NOT_OBSERVED.
        return whois_result

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {
            "domain": domain,
            "error": f"{type(error).__name__}: {error}" if error else "unknown failure",
        }
    result["attempts"] = attempts
    return result
