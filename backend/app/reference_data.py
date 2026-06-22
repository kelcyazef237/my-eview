"""Fixed reference data for categories and vectors.

This module is the single source of truth for the 8 categories and 28 vectors used
in scoring. It is imported by the Alembic seed migration and by the scoring rules
validator to guarantee consistency.
"""

from typing import Any

CATEGORY_ROWS: list[dict[str, Any]] = [
    {"id": 1, "key": "email_trust", "name": "Email Trust & Authentication", "points_total": 140, "scored": True, "parent_group": "Digital Identity", "sort_order": 1},
    {"id": 2, "key": "domain_governance", "name": "Digital Identity & Domain Governance", "points_total": 90, "scored": True, "parent_group": "Digital Identity", "sort_order": 2},
    {"id": 3, "key": "infrastructure_security", "name": "Infrastructure Security", "points_total": 180, "scored": True, "parent_group": "Infrastructure Security", "sort_order": 3},
    {"id": 4, "key": "technology_currency", "name": "Technology Currency", "points_total": 90, "scored": True, "parent_group": "Infrastructure Security", "sort_order": 4},
    {"id": 5, "key": "threat_intelligence", "name": "Threat Intelligence Exposure", "points_total": 270, "scored": True, "parent_group": "Threat Exposure", "sort_order": 5},
    {"id": 6, "key": "asset_visibility", "name": "Asset Visibility & Attack Surface", "points_total": 140, "scored": True, "parent_group": "Attack Surface", "sort_order": 6},
    {"id": 7, "key": "ecosystem_trust", "name": "Ecosystem Trust (Third-Party Dependency)", "points_total": 90, "scored": True, "parent_group": "Ecosystem Trust", "sort_order": 7},
    {"id": 8, "key": "entity_intelligence", "name": "Entity Intelligence", "points_total": 0, "scored": False, "parent_group": None, "sort_order": 8},
]

VECTOR_ROWS: list[dict[str, Any]] = [
    # 1 — Email Trust & Authentication (140)
    {"id": 1, "category_id": 1, "key": "spf_presence", "name": "SPF Presence", "data_source": "DNS TXT", "collection_method": "dnspython", "points_budget": 30, "sort_order": 1},
    {"id": 2, "category_id": 1, "key": "dkim_presence", "name": "DKIM Presence", "data_source": "DNS TXT", "collection_method": "dnspython", "points_budget": 30, "sort_order": 2},
    {"id": 3, "category_id": 1, "key": "dmarc_enforcement", "name": "DMARC Presence + Enforcement", "data_source": "DNS TXT", "collection_method": "dnspython", "points_budget": 80, "sort_order": 3},

    # 2 — Digital Identity & Domain Governance (90)
    {"id": 4, "category_id": 2, "key": "domain_age", "name": "Domain Age", "data_source": "WHOIS/RDAP", "collection_method": "python-whois", "points_budget": 15, "sort_order": 1},
    {"id": 5, "category_id": 2, "key": "domain_expiration", "name": "Domain Expiration Health", "data_source": "WHOIS/RDAP", "collection_method": "python-whois", "points_budget": 30, "sort_order": 2},
    {"id": 6, "category_id": 2, "key": "dnssec_adoption", "name": "DNSSEC Adoption", "data_source": "DNS RRSIG/DS", "collection_method": "dnspython", "points_budget": 20, "sort_order": 3},
    {"id": 28, "category_id": 2, "key": "zone_transfer", "name": "Zone Transfer (AXFR) Exposure", "data_source": "DNS AXFR", "collection_method": "dnspython", "points_budget": 25, "sort_order": 4},

    # 3 — Infrastructure Security (180)
    {"id": 7, "category_id": 3, "key": "tls_version", "name": "TLS Version Strength", "data_source": "Direct TLS handshake", "collection_method": "ssl/cryptography", "points_budget": 40, "sort_order": 1},
    {"id": 8, "category_id": 3, "key": "certificate_health", "name": "Certificate Health", "data_source": "Direct TLS handshake", "collection_method": "ssl/cryptography", "points_budget": 45, "sort_order": 2},
    {"id": 9, "category_id": 3, "key": "security_headers", "name": "Security Headers", "data_source": "Direct HTTPS GET", "collection_method": "httpx", "points_budget": 40, "sort_order": 3},
    {"id": 10, "category_id": 3, "key": "https_enforcement", "name": "HTTPS Enforcement", "data_source": "Direct HTTP/HTTPS GET", "collection_method": "httpx", "points_budget": 30, "sort_order": 4},
    {"id": 11, "category_id": 3, "key": "exposed_admin", "name": "Exposed Admin Interfaces", "data_source": "HEAD-only curated paths", "collection_method": "httpx", "points_budget": 25, "sort_order": 5},

    # 4 — Technology Currency (90)
    {"id": 12, "category_id": 4, "key": "tech_obsolescence", "name": "Technology Obsolescence", "data_source": "Server header + generator meta tag", "collection_method": "httpx + beautifulsoup4", "points_budget": 35, "sort_order": 1},
    {"id": 13, "category_id": 4, "key": "software_version", "name": "Software Version Currency", "data_source": "Server header + generator meta tag + CVE lookup", "collection_method": "httpx + beautifulsoup4", "points_budget": 35, "sort_order": 2},
    {"id": 14, "category_id": 4, "key": "legacy_service", "name": "Legacy Service Exposure", "data_source": "Gated TCP-connect + banner read", "collection_method": "python-nmap", "points_budget": 20, "sort_order": 3},

    # 5 — Threat Intelligence Exposure (270)
    {"id": 15, "category_id": 5, "key": "malware", "name": "Malware", "data_source": "AlienVault OTX API", "collection_method": "httpx", "points_budget": 60, "sort_order": 1},
    {"id": 16, "category_id": 5, "key": "phishing", "name": "Phishing", "data_source": "PhishTank + OpenPhish feeds", "collection_method": "httpx", "points_budget": 60, "sort_order": 2},
    {"id": 17, "category_id": 5, "key": "spam_blacklist", "name": "Spam/DNSBL Listings", "data_source": "DNSBL reverse-IP query", "collection_method": "dnspython", "points_budget": 55, "sort_order": 3},
    {"id": 18, "category_id": 5, "key": "botnet", "name": "Botnet C2", "data_source": "Abuse.ch Feodo Tracker", "collection_method": "local cache", "points_budget": 65, "sort_order": 4},
    {"id": 19, "category_id": 5, "key": "blacklist_aggregate", "name": "Blacklist Aggregate Count", "data_source": "Cross-reference multiple sources", "collection_method": "aggregate", "points_budget": 30, "sort_order": 5},

    # 6 — Asset Visibility & Attack Surface (140)
    {"id": 20, "category_id": 6, "key": "asset_count", "name": "Internet-Facing Asset Count", "data_source": "Certificate Transparency logs", "collection_method": "httpx (crt.sh)", "points_budget": 40, "sort_order": 1},
    {"id": 21, "category_id": 6, "key": "shadow_assets", "name": "Shadow Asset Discovery", "data_source": "CT logs + heuristic matching", "collection_method": "httpx", "points_budget": 55, "sort_order": 2},
    {"id": 22, "category_id": 6, "key": "unmanaged_assets", "name": "Unmanaged Asset Indicators", "data_source": "Re-run TLS + HTTP on subdomains", "collection_method": "reuse collectors", "points_budget": 45, "sort_order": 3},

    # 7 — Ecosystem Trust (90)
    {"id": 23, "category_id": 7, "key": "sri_adoption", "name": "Subresource Integrity (SRI) Adoption", "data_source": "HTML integrity= attributes", "collection_method": "beautifulsoup4", "points_budget": 90, "sort_order": 1},

    # 8 — Entity Intelligence (0)
    {"id": 24, "category_id": 8, "key": "related_domains", "name": "Related Domains", "data_source": "WHOIS registrant correlation", "collection_method": "python-whois", "points_budget": 0, "sort_order": 1},
    {"id": 25, "category_id": 8, "key": "shared_infrastructure", "name": "Shared Infrastructure", "data_source": "Shared ASN/IP lookup", "collection_method": "ipwhois", "points_budget": 0, "sort_order": 2},
    {"id": 26, "category_id": 8, "key": "parent_subsidiary", "name": "Parent/Subsidiary", "data_source": "WHOIS/RDAP registrant org correlation", "collection_method": "python-whois", "points_budget": 0, "sort_order": 3},
    {"id": 27, "category_id": 8, "key": "brand_assets", "name": "Brand-Related Assets", "data_source": "Passive DNS + typosquat heuristics", "collection_method": "dnspython", "points_budget": 0, "sort_order": 4},
]


def validate_reference_data() -> None:
    """Validate that vector budgets per category sum to category totals."""
    category_by_id = {c["id"]: c for c in CATEGORY_ROWS}
    sums: dict[int, int] = {}
    for v in VECTOR_ROWS:
        sums[v["category_id"]] = sums.get(v["category_id"], 0) + v["points_budget"]

    for cid, cat in category_by_id.items():
        total = sums.get(cid, 0)
        if total != cat["points_total"]:
            raise ValueError(
                f"Category {cat['key']} points_total={cat['points_total']} "
                f"but vector budgets sum to {total}"
            )

    scored_total = sum(c["points_total"] for c in CATEGORY_ROWS if c["scored"])
    if scored_total != 1000:
        raise ValueError(f"Scored categories sum to {scored_total}, expected 1000")

    if len(CATEGORY_ROWS) != 8:
        raise ValueError(f"Expected 8 categories, got {len(CATEGORY_ROWS)}")

    if len(VECTOR_ROWS) != 28:
        raise ValueError(f"Expected 28 vectors, got {len(VECTOR_ROWS)}")
