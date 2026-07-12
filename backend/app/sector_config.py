"""Sector / industry-specialization configuration.

Maps sector codes (stored on ``Organization.sector``) to human labels and
per-sector regulatory frameworks. The design principle is **layering**:

1. **Universal baseline** — Cameroon Law 2010/012 (cybersecurity) and
   Law 2024/017 (data protection) apply to *every* organization. They are
   always cited in reports regardless of sector.

2. **Sector overlay** — each sector adds 1–3 sector-specific regulations
   on top of the baseline. This keeps the report from being choked with
   every regulation at once while still making it sector-relevant.

3. **Cross-cutting normalization** — regulations that recur across
   sectors (e.g. ISO 27001, PCI DSS) are defined once and referenced by
   multiple sectors, so the text stays consistent.
"""

from typing import Any

# ── Sector catalogue ────────────────────────────────────────────────
# Ordered list of (code, label) for the admin dropdown.
# ``general`` is the fallback when no sector is selected.
SECTORS: list[dict[str, str]] = [
    {"code": "general",        "label": "General / Unspecified"},
    {"code": "finance",        "label": "Finance & Microfinance"},
    {"code": "fintech",        "label": "Fintech & Payments"},
    {"code": "health",         "label": "Health & Medical"},
    {"code": "education",      "label": "Education & Research"},
    {"code": "telecom",        "label": "Telecom & ISP"},
    {"code": "ecommerce",      "label": "E-Commerce & Retail"},
    {"code": "government",     "label": "Government & Public Sector"},
]

SECTOR_CODES = [s["code"] for s in SECTORS]
SECTOR_LABELS = {s["code"]: s["label"] for s in SECTORS}


def sector_label(code: str | None) -> str:
    """Return a human label for a sector code, or 'General' if unknown."""
    if not code:
        return SECTOR_LABELS["general"]
    return SECTOR_LABELS.get(code, code.replace("_", " ").title())


# ── Regulation definitions ───────────────────────────────────────────
# Each regulation is a reusable dict so sectors reference the same object
# (no text duplication). ``short`` is the card code, ``title`` the card
# heading, ``body`` the card description, ``tia_ref`` the one-line string
# injected into TIA ``regulatory_relevance`` slots.

_UNIVERSAL = [
    {
        "short": "ANTIC 2010/012",
        "title": "Cybersecurity & Cybercrime Law",
        "body": "Law No. 2010/012 establishes baseline obligations for system integrity, electronic communications security, and incident reporting applicable to all organizations operating in Cameroon.",
        "tia_ref": "ANTIC Law No. 2010/012",
    },
    {
        "short": "Law 2024/017",
        "title": "Data Protection — June 2026 Deadline",
        "body": "Law No. 2024/017 imposes technical and organizational security measures on institutions processing personal data. Compliance deadline: 23 June 2026.",
        "tia_ref": "Law No. 2024/017 (Data Protection)",
    },
]

_SECTOR_REGS: dict[str, list[dict[str, Any]]] = {
    "general": [],  # universal baseline only

    "finance": [
        {
            "short": "COBAC",
            "title": "Banking Commission — Operational Risk",
            "body": "COBAC regulations (R-2016/04 internal control, R-2008/01 BCP) establish expectations for information system integrity, access controls, and operational risk management for CEMAC financial institutions.",
            "tia_ref": "COBAC operational risk management obligations",
        },
        {
            "short": "PCI DSS",
            "title": "Payment Card Industry Data Security Standard",
            "body": "PCI DSS v4.0 requirements for encrypting cardholder data in transit (Req 4), secure networks (Req 1), and vulnerability management (Req 6) apply to institutions handling payment cards.",
            "tia_ref": "PCI DSS v4.0 (Req 4 — transmission security, Req 6 — secure systems)",
        },
    ],

    "fintech": [
        {
            "short": "COBAC R-04/18",
            "title": "Payment Services & E-Money",
            "body": "COBAC Regulation R-04/18 and CEMAC Regulation 01/11 govern electronic money issuance and payment services, requiring robust IT security for payment platforms and mobile money operations.",
            "tia_ref": "COBAC R-04/18 (payment services) and CEMAC Reg 01/11 (e-money)",
        },
        {
            "short": "PCI DSS",
            "title": "Payment Card Industry — SAQ-A",
            "body": "PCI DSS SAQ-A applies to e-commerce / hosted payment pages: all cardholder data must be encrypted in transit (Req 4.1) and payment forms must be served over TLS 1.2+.",
            "tia_ref": "PCI DSS SAQ-A (Req 4.1 — strong cryptography on payment pages)",
        },
        {
            "short": "MINFI 2024",
            "title": "E-Payment Licensing Decree",
            "body": "MINFI decree of 28 Feb 2024 requires local database hosting and functional separation of telecom MMO subsidiaries for licensed e-payment providers in Cameroon.",
            "tia_ref": "MINFI e-payment licensing decree (Feb 2024)",
        },
    ],

    "health": [
        {
            "short": "HIPAA SR",
            "title": "HIPAA Security Rule (global reference)",
            "body": "HIPAA Security Rule §164.312 establishes technical safeguards for electronic health information: transmission security (e1), access control (a1), and integrity (c1). Referenced globally as the health-data security benchmark.",
            "tia_ref": "HIPAA Security Rule §164.312 (transmission security, access control)",
        },
        {
            "short": "ISO 27799",
            "title": "Health Informatics Security",
            "body": "ISO 27799 provides sector-specific guidelines for protecting personal health information using the ISO 27002 control set — cryptography (Cl 7.4), communications security (Cl 9).",
            "tia_ref": "ISO 27799 (health information security — Cl 7.4 cryptography, Cl 9 comms)",
        },
    ],

    "education": [
        {
            "short": "FERPA",
            "title": "Student Records Protection (global reference)",
            "body": "FERPA 34 CFR Part 99 establishes the global benchmark for protecting student education records, requiring institutional controls for PII in transit and at rest.",
            "tia_ref": "FERPA 34 CFR Part 99 (student record protection)",
        },
        {
            "short": "ISO 27001",
            "title": "ISMS for Educational Institutions",
            "body": "ISO 27001/27002 Annex A controls applied to education: network security (A.8.20), cryptography (A.8.24), and information transfer (A.5.14) for LMS and student portals.",
            "tia_ref": "ISO 27001/27002 Annex A (A.8.20 network security, A.8.24 cryptography)",
        },
    ],

    "telecom": [
        {
            "short": "ITU-T X.805",
            "title": "Telecom Security Architecture",
            "body": "ITU-T X.805 defines a security architecture for end-to-end telecom networks covering access control, authentication, data confidentiality, and integrity across all network layers.",
            "tia_ref": "ITU-T X.805 (telecom security architecture)",
        },
        {
            "short": "ISO 27011",
            "title": "Telecom ISMS Guidelines",
            "body": "ISO 27011 provides telecom-specific guidance on top of ISO 27002: subscriber data protection (Cl 13), network architecture security, and operations monitoring.",
            "tia_ref": "ISO 27011 (telecom — subscriber data protection, Cl 13)",
        },
    ],

    "ecommerce": [
        {
            "short": "PCI DSS",
            "title": "Payment Card Industry — Merchant",
            "body": "PCI DSS applies to e-commerce merchants: protect stored cardholder data (Req 3), encrypt transmission (Req 4), and maintain secure web applications (Req 6).",
            "tia_ref": "PCI DSS v4.0 (Req 4 — transmission security, Req 6 — secure apps)",
        },
        {
            "short": "OWASP ASVS",
            "title": "Application Security Verification",
            "body": "OWASP ASVS Level 2 provides verification requirements for e-commerce web applications: TLS enforcement (V9), authentication (V2), and transport layer protection.",
            "tia_ref": "OWASP ASVS (V9 — transport layer, V2 — authentication)",
        },
    ],

    "government": [
        {
            "short": "NIST 800-53",
            "title": "Federal System Security Controls",
            "body": "NIST SP 800-53 Rev 5 controls for government systems: transmission confidentiality (SC-8), boundary protection (SC-7), and system integrity (SI-7). Global reference for public-sector cyber posture.",
            "tia_ref": "NIST SP 800-53 Rev 5 (SC-8 transmission, SC-7 boundary, SI-7 integrity)",
        },
        {
            "short": "ISO 27001",
            "title": "ISMS for Public Administration",
            "body": "ISO 27001/27002 applied to government: information classification (A.5.12), network security (A.8.20), and cryptography (A.8.24) for citizen-facing digital services.",
            "tia_ref": "ISO 27001/27002 (A.5.12 classification, A.8.20 network security)",
        },
    ],
}


def regulations_for_sector(sector: str | None) -> list[dict[str, Any]]:
    """Return the regulation cards for a sector: universal baseline + sector overlay."""
    code = sector if sector in _SECTOR_REGS else "general"
    return list(_UNIVERSAL) + list(_SECTOR_REGS.get(code, []))


def tia_regulatory_text(sector: str | None) -> str:
    """Build the ``regulatory_relevance`` string injected into TIA templates.

    Concatenates the short ``tia_ref`` lines for the sector's regulations
    so a TIA slot reads e.g.:
    ``Relevant to ANTIC Law No. 2010/012, Law No. 2024/017 (Data Protection),
    and COBAC operational risk management obligations. ...``

    The universal baseline is always present; sector regs append after it.
    """
    regs = regulations_for_sector(sector)
    refs = [r["tia_ref"] for r in regs]
    if len(refs) == 1:
        return refs[0]
    if len(refs) == 2:
        return f"{refs[0]} and {refs[1]}"
    return ", ".join(refs[:-1]) + f", and {refs[-1]}"