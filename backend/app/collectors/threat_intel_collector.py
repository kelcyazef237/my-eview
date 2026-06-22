"""Threat intelligence collector using free feeds and local cache."""

from datetime import datetime, timezone, timedelta
from typing import Any

import dns.resolver
import httpx
from sqlalchemy.orm import Session

from app.collectors.base import get_bound_httpx_client, run_in_thread, with_retry
from app.collectors.dnsbl_collector import query as query_dnsbl
from app.config import get_settings
from app.services.threat_feed_cache import get_cache

settings = get_settings()

ACTIVE_WINDOW_DAYS = 180


def _domain_or_subdomain_in_feed(domain: str, feed: list[str]) -> bool:
    domain_lower = domain.lower()
    for entry in feed:
        entry_lower = entry.lower().strip()
        if not entry_lower:
            continue
        if entry_lower == domain_lower or entry_lower.endswith(f".{domain_lower}"):
            return True
    return False


def _resolve_a(domain: str) -> list[str]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    try:
        ans = resolver.resolve(domain, "A")
        return [str(r) for r in ans]
    except Exception:
        return []


def _classify_age(pulse_dates: list[datetime]) -> str:
    if not pulse_dates:
        return "none"
    now = datetime.now(timezone.utc)
    active_cutoff = now - timedelta(days=ACTIVE_WINDOW_DAYS)
    if any(d > active_cutoff for d in pulse_dates):
        return "active"
    return "historical"


def _parse_iso_dates(dates: list[str]) -> list[datetime]:
    parsed = []
    for d in dates:
        try:
            dt = datetime.fromisoformat(d.replace("Z", "+00:00"))
            parsed.append(dt.astimezone(timezone.utc))
        except Exception:
            pass
    return parsed


async def _query_otx_domain(domain: str) -> dict:
    key = settings.otx_api_key
    if not key:
        return {"domain": domain, "skipped": True, "reason": "no_api_key"}

    headers = {"X-OTX-API-KEY": key}
    base = "https://otx.alienvault.com/api/v1"

    async def _run() -> dict:
        async with get_bound_httpx_client(timeout=20, headers=headers, follow_redirects=True) as client:
            general = await client.get(f"{base}/indicators/domain/{domain}/general")
            general.raise_for_status()
            general_data = general.json()

            malware = await client.get(f"{base}/indicators/domain/{domain}/malware")
            malware.raise_for_status()
            malware_data = malware.json()

        pulse_dates = []
        for pulse in general_data.get("pulse_info", {}).get("pulses", []):
            if pulse.get("modified"):
                pulse_dates.append(pulse["modified"])
            elif pulse.get("created"):
                pulse_dates.append(pulse["created"])

        malware_count = len(malware_data.get("data", []))
        return {
            "domain": domain,
            "pulse_count": general_data.get("pulse_info", {}).get("count", 0),
            "malware_count": malware_count,
            "pulse_dates": pulse_dates,
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {"domain": domain, "error": str(error)}
    result["attempts"] = attempts
    return result


def _check_feeds_for_domain(domain: str, db: Session) -> dict:
    phishtank = get_cache(db, "phishtank", "http://data.phishtank.com/data/online-valid.json")
    openphish = get_cache(db, "openphish", "https://openphish.com/feed.txt")
    feodo = get_cache(db, "feodo", "https://feodotracker.abuse.ch/downloads/ipblocklist.csv")

    pt_list = phishtank["payload"].get("urls", []) if phishtank else []
    op_list = openphish["payload"].get("urls", []) if openphish else []
    feodo_ips = feodo["payload"].get("ips", []) if feodo else []

    return {
        "phishing": {
            "phishtank_listed": _domain_or_subdomain_in_feed(domain, pt_list),
            "openphish_listed": _domain_or_subdomain_in_feed(domain, op_list),
        },
        "botnet": {
            "domain_ips": _resolve_a(domain),
            "feodo_ips": feodo_ips,
        },
    }


async def collect(domain: str, db: Session) -> dict:
    """Collect threat-intel evidence for a domain.

    This is async for the live portions (OTX, DNSBL) but uses a synchronous DB
    session for cache lookups.
    """
    otx = await _query_otx_domain(domain)
    dnsbl_results = []
    for ip in _resolve_a(domain):
        dnsbl_results.append(await query_dnsbl(ip))

    feed_check = await run_in_thread(_check_feeds_for_domain, domain, db)

    # Feodo check: any domain IP in cached Feodo list?
    feodo_ips = set(feed_check["botnet"]["feodo_ips"])
    domain_ips = feed_check["botnet"]["domain_ips"]
    feodo_listed = any(ip in feodo_ips for ip in domain_ips)

    # OTX age classification
    otx_dates = _parse_iso_dates(otx.get("pulse_dates", []))
    otx_activity = _classify_age(otx_dates) if otx.get("pulse_count", 0) or otx.get("malware_count", 0) else "none"
    malware_activity = "active" if otx.get("malware_count", 0) > 0 else "none"

    # Phishing classification
    phishing_listed = feed_check["phishing"]["phishtank_listed"] or feed_check["phishing"]["openphish_listed"]
    phishing_activity = "active" if phishing_listed else "none"

    # DNSBL classification
    listed_count = sum(r.get("listed_count", 0) for r in dnsbl_results)
    spam_state = "none" if listed_count == 0 else ("warn" if listed_count == 1 else "fail")

    # Aggregate blacklist count across all signals
    aggregate_count = 0
    if otx.get("pulse_count", 0) > 0:
        aggregate_count += 1
    if malware_activity == "active":
        aggregate_count += 1
    if phishing_listed:
        aggregate_count += 1
    aggregate_count += listed_count
    if feodo_listed:
        aggregate_count += 1

    return {
        "domain": domain,
        "otx": otx,
        "dnsbl": dnsbl_results,
        "feed_check": feed_check,
        "derived": {
            "malware_activity": malware_activity,
            "phishing_activity": phishing_activity,
            "spam_listed_count": listed_count,
            "botnet_listed": feodo_listed,
            "blacklist_aggregate_count": aggregate_count,
        },
    }
