"""DNSBL collector for spam/blacklist reputation."""

import dns.exception
import dns.resolver

from app.collectors.base import with_retry


DNSBL_ZONES = [
    "zen.spamhaus.org",
    "multi.surbl.org",
    "b.barracudacentral.org",
]


def _reverse_octets(ip: str) -> str:
    return ".".join(reversed(ip.split(".")))


def _query_zone(ip: str, zone: str) -> dict:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    query = f"{_reverse_octets(ip)}.{zone}"
    try:
        ans = resolver.resolve(query, "A")
        codes = [str(r) for r in ans]
        return {"zone": zone, "listed": True, "return_codes": codes}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return {"zone": zone, "listed": False, "return_codes": []}
    except dns.exception.Timeout:
        return {"zone": zone, "listed": False, "return_codes": [], "timeout": True}


async def query(ip: str) -> dict:
    async def _run() -> dict:
        results = [_query_zone(ip, zone) for zone in DNSBL_ZONES]
        listed = [r for r in results if r["listed"]]
        return {
            "ip": ip,
            "zones": results,
            "listed_count": len(listed),
            "listed_zones": [r["zone"] for r in listed],
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {"ip": ip, "error": str(error)}
    result["attempts"] = attempts
    return result
