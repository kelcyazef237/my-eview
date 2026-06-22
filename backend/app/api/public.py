from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.organization import Organization
from app.models.score import Score
from app.scoring.shield_mapper import shield_for_score
from app.services.rate_limit import public_lookup_domain_allowed, public_lookup_ip_allowed
from app.services.scan_orchestrator import run_scan

router = APIRouter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _score_response(score: Score, domain: str, scan_status: str | None = None) -> dict:
    shield = shield_for_score(score.overall_score)
    resp = {
        "domain": domain,
        "org_name": score.organization.name,
        "overall_score": score.overall_score,
        "shield_tier": shield.tier,
        "shield_label": shield.short_label,
        "band": shield.band,
        "outlook": score.outlook,
        "sector_benchmark": None,
        "ruleset_version": score.ruleset_version,
        "computed_at": score.computed_at.isoformat(),
    }
    if scan_status and scan_status == "incomplete":
        resp["warning"] = "Scan completed but some vectors could not be observed. Score may be incomplete."
    return resp


@router.get("/lookup/{domain}")
async def lookup_domain(domain: str, request: Request, db: Session = Depends(get_db)):
    domain = domain.lower().strip()
    score = (
        db.query(Score)
        .join(Organization, Score.org_id == Organization.id)
        .filter(Organization.primary_domain == domain)
        .order_by(Score.computed_at.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No score available. Trigger a scan first.")
    return _score_response(score, domain, score.scan_run.status)


@router.post("/lookup/{domain}")
async def trigger_lookup(domain: str, request: Request, db: Session = Depends(get_db)):
    domain = domain.lower().strip()
    client_ip = _client_ip(request)

    if not public_lookup_domain_allowed(domain):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Scan limit reached for this domain.")
    if not public_lookup_ip_allowed(client_ip):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Scan limit reached for this IP.")

    scan_run = await run_scan(db, domain, is_full_report=False)
    score = db.query(Score).filter(Score.scan_run_id == scan_run.id).first()
    if not score:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Scan failed to produce a score. Check server logs for collector errors.",
        )
    return _score_response(score, domain, scan_run.status)
