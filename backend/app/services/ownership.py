"""Domain ownership verification service (DNS TXT and email)."""

import secrets
from datetime import datetime, timezone

import dns.resolver
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.ownership_verification import OwnershipVerification


VERIFICATION_PREFIX = "myeview-verify"


def start_verification(db: Session, org_id: str, method: str) -> OwnershipVerification:
    token = secrets.token_urlsafe(32)
    verification = OwnershipVerification(
        org_id=org_id,
        method=method,
        token=token,
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification


def get_pending_verification(db: Session, org_id: str, method: str) -> OwnershipVerification | None:
    return (
        db.query(OwnershipVerification)
        .filter_by(org_id=org_id, method=method, verified_at=None)
        .order_by(OwnershipVerification.created_at.desc())
        .first()
    )


def _dns_txt_records(name: str) -> list[str]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 5.0
    try:
        ans = resolver.resolve(name, "TXT")
    except Exception:
        return []
    return ["".join(s.decode(errors="replace") for s in r.strings) for r in ans]


def check_dns_verification(db: Session, org: Organization) -> bool:
    verification = get_pending_verification(db, str(org.id), "dns_txt")
    if not verification:
        return org.ownership_verified

    records = _dns_txt_records(org.primary_domain)
    expected = f"{VERIFICATION_PREFIX}={verification.token}"
    if expected in records:
        verification.verified_at = datetime.now(timezone.utc)
        org.ownership_verified = True
        db.commit()
        return True
    return False


def verify_email_token(db: Session, token: str) -> Organization | None:
    verification = (
        db.query(OwnershipVerification)
        .filter_by(token=token, method="email", verified_at=None)
        .first()
    )
    if not verification:
        return None
    org = db.query(Organization).filter(Organization.id == verification.org_id).first()
    if not org:
        return None
    verification.verified_at = datetime.now(timezone.utc)
    org.ownership_verified = True
    db.commit()
    return org


def verification_instructions(org: Organization, verification: OwnershipVerification) -> dict:
    if verification.method == "dns_txt":
        return {
            "method": "dns_txt",
            "token": verification.token,
            "txt_record": f"{VERIFICATION_PREFIX}={verification.token}",
            "domain": org.primary_domain,
            "instructions": f"Create a TXT record on {org.primary_domain} with value: {VERIFICATION_PREFIX}={verification.token}",
        }
    return {
        "method": "email",
        "token": verification.token,
        "addresses": [f"admin@{org.primary_domain}", f"security@{org.primary_domain}"],
    }
