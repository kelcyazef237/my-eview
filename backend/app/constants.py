from enum import Enum


class VectorState(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_OBSERVED = "NOT_OBSERVED"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    FAILED = "failed"


class AssetType(str, Enum):
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP = "ip"


class UserRole(str, Enum):
    PUBLIC = "public"
    OWNER = "owner"
    OWNER_TECHNICAL = "owner_technical"
    OPS = "ops"


class VerificationMethod(str, Enum):
    DNS_TXT = "dns_txt"
    EMAIL = "email"


class RulesetVersion(str, Enum):
    V1 = "v1"


class TiaTemplateSlot(str, Enum):
    TECHNICAL_OBSERVATION = "technical_observation"
    BUSINESS_IMPACT = "business_impact"
    STAKEHOLDERS_AFFECTED = "stakeholders_affected"
    REGULATORY_RELEVANCE = "regulatory_relevance"
    RECOMMENDED_ACTION = "recommended_action"


# Fixed stakeholder tags allowed in TIA output
STAKEHOLDER_TAGS = {"Customers", "Employees", "Business Partners", "Regulators"}

# Common DKIM selectors probed when no selector is known
DKIM_SELECTORS = ("default", "google", "selector1", "selector2", "mail")

# Curated admin / sensitive paths probed with HEAD-only requests
ADMIN_PATHS = (
    "/admin",
    "/wp-admin",
    "/phpmyadmin",
    "/pma",
    "/adminer",
    "/manager",
    "/api/admin",
    "/console",
    "/.env",
    "/config",
    "/swagger",
    "/api/swagger",
    "/login",
    "/wp-login.php",
)

# Security headers checked for the Security Headers vector
CRITICAL_SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
)

# Legacy ports checked in the gated Verified port-scan collector
LEGACY_PORTS = {
    21: "ftp",
    23: "telnet",
    25: "smtp",
    22: "ssh",
}

# Thresholds
NOT_OBSERVED_THRESHOLD_RATIO = 0.15
THREAT_INTEL_ACTIVE_MONTHS = 6

# Cameroon regulatory citations
REGULATORY_CITATIONS = {
    "antic_2010_012": "ANTIC Law No. 2010/012 (Cybersecurity and Cybercrime), Arts. 7, 13, 14, 32, 61",
    "data_protection_2024_017": "Law No. 2024/017 (Data Protection), Arts. 22, 27, 32, 33; compliance deadline 23 June 2026",
    "cobac_operational_risk": "COBAC operational risk management obligations for information system integrity and access controls",
}

REGULATORY_DISCLAIMER = (
    "Regulatory determinations require qualified legal and compliance advisors. "
    "MYEVIEW identifies external exposure signals that may indicate areas warranting compliance review."
)
