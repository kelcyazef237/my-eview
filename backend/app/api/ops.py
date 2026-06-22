from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import require_ops
from app.database import get_db
from app.models.organization import Organization
from app.models.scan_run import ScanRun
from app.models.user import User
from app.services.scan_orchestrator import run_scan

router = APIRouter()


class RescanRequest(BaseModel):
    domain: str


@router.get("/orgs")
def list_orgs(user: User = Depends(require_ops), db: Session = Depends(get_db)):
    orgs = db.query(Organization).all()
    return [
        {
            "id": str(o.id),
            "name": o.name,
            "domain": o.primary_domain,
            "ownership_verified": o.ownership_verified,
            "created_at": o.created_at.isoformat(),
        }
        for o in orgs
    ]


@router.get("/scan-runs")
def list_scan_runs(user: User = Depends(require_ops), db: Session = Depends(get_db)):
    runs = db.query(ScanRun).order_by(ScanRun.started_at.desc()).limit(50).all()
    return [
        {
            "id": str(r.id),
            "org_id": str(r.org_id),
            "domain": r.organization.primary_domain,
            "status": r.status,
            "is_full_report": r.is_full_report,
            "started_at": r.started_at.isoformat(),
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        }
        for r in runs
    ]


@router.post("/rescan")
async def ops_rescan(payload: RescanRequest, user: User = Depends(require_ops), db: Session = Depends(get_db)):
    scan_run = await run_scan(db, payload.domain.lower(), is_full_report=False)
    return {"scan_run_id": str(scan_run.id), "status": scan_run.status}
