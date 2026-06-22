"""WHOIS/RDAP collector for domain age and expiration."""

import asyncio
from datetime import datetime, timezone

import whois

from app.collectors.base import run_in_thread, with_retry


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
        return await run_in_thread(_whois_raw, domain)

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {"domain": domain, "error": str(error)}
    result["attempts"] = attempts
    return result
