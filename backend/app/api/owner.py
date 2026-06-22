from enum import Enum
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner, require_owner_technical, resolve_org_id
from app.database import get_db
from app.models.asset import Asset
from app.models.category_score import CategoryScore
from app.models.organization import Organization
from app.models.raw_evidence import RawEvidence
from app.models.scan_run import ScanRun
from app.models.score import Score
from app.models.score_history import ScoreHistory
from app.models.tia_entry import TiaEntry
from app.models.user import User
from app.models.vector_finding import VectorFinding
from app.services.ownership import check_dns_verification, start_verification, verification_instructions, verify_email_token
from app.services.scan_orchestrator import run_scan

router = APIRouter()


class VerificationStart(BaseModel):
    method: str  # dns_txt | email


def _build_entity_intelligence(db: Session, scan_run_id: str, org_id: str) -> dict:
    """Build the unscored Entity Intelligence section from raw evidence."""
    # Discovered assets from CT logs
    assets = db.query(Asset).filter_by(org_id=org_id).all()
    subdomains = [a.value for a in assets if a.type == "subdomain"]

    # WHOIS evidence for registrant/registrar info
    whois_evidence = (
        db.query(RawEvidence)
        .filter_by(scan_run_id=scan_run_id, collector_name="whois")
        .first()
    )
    whois_data = whois_evidence.raw_payload if whois_evidence else {}

    return {
        "scored": False,
        "label": "Not Scored — Contextual Intelligence Only",
        "related_domains": {
            "count": len(subdomains),
            "items": subdomains[:20],
        },
        "shared_infrastructure": {
            "registrar": whois_data.get("registrar"),
            "name_servers": whois_data.get("name_servers") or [],
        },
        "parent_subsidiary": {
            "registrant": whois_data.get("registrant"),
        },
        "brand_assets": {
            "discovered_via": "Certificate Transparency logs",
            "count": len(subdomains),
        },
    }


@router.get("/dashboard")
async def dashboard(user: User = Depends(require_owner), db: Session = Depends(get_db)):
    user_org_id = resolve_org_id(user, db)

    score = (
        db.query(Score)
        .filter(Score.org_id == user_org_id)
        .order_by(Score.computed_at.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No score available for this organization")

    category_scores = (
        db.query(CategoryScore)
        .filter_by(scan_run_id=score.scan_run_id)
        .all()
    )
    tia_entries = (
        db.query(TiaEntry)
        .filter_by(scan_run_id=score.scan_run_id)
        .all()
    )

    # Score history for trend chart
    history = (
        db.query(ScoreHistory)
        .filter_by(org_id=user_org_id)
        .order_by(ScoreHistory.computed_at.desc())
        .limit(24)
        .all()
    )

    # Entity intelligence (unscored, displayed separately)
    entity_intel = _build_entity_intelligence(db, str(score.scan_run_id), str(user_org_id))

    return {
        "org": {
            "id": str(score.organization.id),
            "name": score.organization.name,
            "domain": score.organization.primary_domain,
            "ownership_verified": score.organization.ownership_verified,
        },
        "score": {
            "scan_run_id": str(score.scan_run_id),
            "overall": score.overall_score,
            "shield_tier": score.shield_tier,
            "outlook": score.outlook,
            "computed_at": score.computed_at.isoformat(),
            "is_full_report": score.is_full_report,
        },
        "categories": [
            {
                "category_id": str(cs.category.id),
                "category_key": cs.category.key,
                "category_name": cs.category.name,
                "points_total": cs.points_total,
                "points_lost": cs.points_lost,
                "points_remaining": cs.points_remaining,
                "parent_group": cs.category.parent_group,
            }
            for cs in category_scores
        ],
        "tia": [
            {
                "category_id": str(te.category.id),
                "category_key": te.category.key,
                "template_id": te.template_id,
                "rendered_text": te.rendered_text,
            }
            for te in tia_entries
        ],
        "history": [
            {
                "scan_run_id": str(h.scan_run_id),
                "overall_score": h.overall_score,
                "is_full_report": h.is_full_report,
                "computed_at": h.computed_at.isoformat(),
            }
            for h in reversed(history)
        ],
        "entity_intelligence": entity_intel,
        "user_role": user.role,
    }


@router.get("/technical")
async def technical_view(user: User = Depends(require_owner_technical), db: Session = Depends(get_db)):
    user_org_id = resolve_org_id(user, db)

    score = (
        db.query(Score)
        .filter(Score.org_id == user_org_id)
        .order_by(Score.computed_at.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No score available")

    findings = (
        db.query(VectorFinding)
        .filter_by(scan_run_id=score.scan_run_id)
        .all()
    )

    return {
        "scan_run_id": str(score.scan_run_id),
        "overall_score": score.overall_score,
        "shield_tier": score.shield_tier,
        "vectors": [
            {
                "vector_key": vf.vector.key,
                "vector_name": vf.vector.name,
                "category_key": vf.vector.category.key,
                "state": vf.state,
                "evidence_ref": vf.evidence_ref,
            }
            for vf in findings
        ],
    }


@router.get("/history")
def score_history(user: User = Depends(require_owner), db: Session = Depends(get_db)):
    user_org_id = resolve_org_id(user, db)

    history = (
        db.query(ScoreHistory)
        .filter_by(org_id=user_org_id)
        .order_by(ScoreHistory.computed_at.desc())
        .limit(24)
        .all()
    )

    return [
        {
            "scan_run_id": str(h.scan_run_id),
            "overall_score": h.overall_score,
            "is_full_report": h.is_full_report,
            "computed_at": h.computed_at.isoformat(),
        }
        for h in history
    ]


@router.post("/verify/start")
def start_verification_flow(payload: VerificationStart, user: User = Depends(require_owner), db: Session = Depends(get_db)):
    user_org_id = resolve_org_id(user, db)
    org = db.query(Organization).filter(Organization.id == user_org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    verification = start_verification(db, str(org.id), payload.method)
    return verification_instructions(org, verification)


@router.get("/verify/status")
def verification_status(user: User = Depends(require_owner), db: Session = Depends(get_db)):
    user_org_id = resolve_org_id(user, db)
    org = db.query(Organization).filter(Organization.id == user_org_id).first()
    verified = check_dns_verification(db, org)
    return {
        "ownership_verified": org.ownership_verified,
        "just_verified": verified,
    }


@router.get("/verify/email")
def verify_email(token: str, db: Session = Depends(get_db)):
    org = verify_email_token(db, token)
    if not org:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    return {"ownership_verified": True, "domain": org.primary_domain}


@router.post("/rescan")
async def rescan(user: User = Depends(require_owner), db: Session = Depends(get_db)):
    user_org_id = resolve_org_id(user, db)
    org = db.query(Organization).filter(Organization.id == user_org_id).first()
    scan_run = await run_scan(db, org.primary_domain, is_full_report=False)
    return {"scan_run_id": str(scan_run.id), "status": scan_run.status}
