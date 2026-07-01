"""DNS collector for SPF, DKIM, DMARC, DNSSEC, and Zone Transfer evidence."""

import asyncio

import dns.exception
import dns.resolver
import dns.query
import dns.zone

from app.constants import DKIM_SELECTORS
from app.collectors.base import run_in_thread, with_retry


def _txt_records(name: str) -> list[str]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    try:
        ans = resolver.resolve(name, "TXT")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers):
        return []
    records = []
    for rdata in ans:
        txt = "".join(s.decode(errors="replace") for s in rdata.strings)
        records.append(txt)
    return records


def _has_spf(domain: str) -> bool:
    return any(r.strip().startswith("v=spf1") for r in _txt_records(domain))


def _has_dkim(domain: str) -> bool:
    for selector in DKIM_SELECTORS:
        name = f"{selector}._domainkey.{domain}"
        for r in _txt_records(name):
            if r.strip().startswith("v=DKIM1"):
                return True
    return False


def _dmarc_record(domain: str) -> str | None:
    records = _txt_records(f"_dmarc.{domain}")
    for r in records:
        if r.strip().startswith("v=DMARC1"):
            return r.strip()
    return None


def _dmarc_policy(record: str | None) -> str:
    if not record:
        return "absent"
    lower = record.lower()
    if "p=reject" in lower:
        return "reject"
    if "p=quarantine" in lower:
        return "quarantine"
    if "p=none" in lower:
        return "none"
    return "invalid"


def _dnssec_signals(domain: str) -> dict:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    signals = {"ds": False, "dnskey": False, "rrsig": False}
    for rtype in ("DS", "DNSKEY"):
        try:
            ans = resolver.resolve(domain, rtype)
            if ans.rrset:
                signals[rtype.lower()] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers):
            pass
    # RRSIG records are usually returned alongside DNSKEY/DS answers; check for them indirectly.
    try:
        ans = resolver.resolve(domain, "DNSKEY", want_dnssec=True)
        if ans.response and ans.response.answer:
            for rrset in ans.response.answer:
                if rrset.rdtype == 46:  # RRSIG
                    signals["rrsig"] = True
    except Exception:
        pass
    return signals


def _authoritative_nameservers(domain: str) -> list[str]:
    """Resolve the authoritative NS records for a domain."""
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    try:
        ans = resolver.resolve(domain, "NS")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers):
        return []
    return [str(rdata.target).rstrip(".") for rdata in ans]


def _resolve_ns_ip(ns_hostname: str) -> str | None:
    """Resolve a nameserver hostname to its IPv4 address."""
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    try:
        ans = resolver.resolve(ns_hostname, "A")
        for rdata in ans:
            return str(rdata)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers):
        pass
    return None


def _probe_one_ns(ns_ip: str, domain: str) -> str | None:
    """Probe a single nameserver for AXFR allowance. Returns ns_ip on allow.

    Runs in a thread; AXFR is a blocking dnspython call. `lifetime=15` (down
    from 30) because the rare 30s response is more often a network issue
    than a legitimate slow server.
    """
    try:
        dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=5, lifetime=15))
        return ns_ip
    except Exception:
        return None


async def _zone_transfer_status(domain: str) -> dict:
    """Test AXFR against every authoritative nameserver in parallel.

    Returns {"tested": int, "allowed": list[str], "refused": list[str]}.
    PASS if all refuse, FAIL if any allows.

    dns.query.xfr requires an IP address (not a hostname), so we resolve
    each NS hostname to its IP first, then probe all IPs concurrently.
    """
    nameservers = _authoritative_nameservers(domain)
    if not nameservers:
        return {"tested": 0, "allowed": [], "refused": []}

    # Resolve NS hostnames to IPs in parallel (each is a blocking resolver call).
    ips = await asyncio.gather(
        *(run_in_thread(_resolve_ns_ip, ns) for ns in nameservers)
    )

    # Probe each IP for AXFR in parallel.
    results = await asyncio.gather(
        *(run_in_thread(_probe_one_ns, ip, domain) for ip in ips if ip)
    )
    allowed_ips = {r for r in results if r}

    # Map back to NS hostnames for the result.
    allowed = [ns for ns, ip in zip(nameservers, ips) if ip in allowed_ips]
    refused = [
        ns for ns, ip in zip(nameservers, ips) if ip and ip not in allowed_ips
    ]
    no_ip = [ns for ns, ip in zip(nameservers, ips) if not ip]

    return {
        "tested": len(nameservers),
        "allowed": allowed,
        "refused": refused + no_ip,
    }


async def collect(domain: str) -> dict:
    """Collect DNS-based evidence for a domain."""

    async def _run() -> dict:
        spf = _has_spf(domain)
        dkim = _has_dkim(domain)
        dmarc_record = _dmarc_record(domain)
        dmarc_policy = _dmarc_policy(dmarc_record)
        dnssec = _dnssec_signals(domain)
        zone_transfer = await _zone_transfer_status(domain)
        return {
            "domain": domain,
            "spf_present": spf,
            "dkim_present": dkim,
            "dmarc_record": dmarc_record,
            "dmarc_policy": dmarc_policy,
            "dnssec": dnssec,
            "zone_transfer": zone_transfer,
        }

    result, attempts, error = await with_retry(_run)
    if result is None:
        result = {
            "domain": domain,
            "error": str(error),
        }
    result["attempts"] = attempts
    return result
