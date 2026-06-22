from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner, resolve_org_id
from app.database import get_db
from app.models.organization import Organization
from app.models.scan_run import ScanRun
from app.models.user import User
from app.tasks.celery_app import app as celery_app

router = APIRouter()


class PortscanResponse(BaseModel):
    status: str
    scan_run_id: str
    task_id: str | None = None
    detail: str | None = None


@router.post("/portscan", response_model=PortscanResponse)
async def trigger_verified_portscan(
    org_id: str | None = Query(None),
    user: User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    """Trigger the verified-tier port-scan for the current (or specified) organization.

    Accessible to owner, owner_technical, ops, and global_admin.
    The task runs on the dedicated ``verified`` Celery queue and re-scores the
    most recent scan run once the port-scan evidence is collected.
    """
    user_org_id = resolve_org_id(user, db, org_id=org_id)

    org = db.query(Organization).filter(Organization.id == user_org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    scan_run = (
        db.query(ScanRun)
        .filter_by(org_id=org.id)
        .order_by(ScanRun.started_at.desc())
        .first()
    )
    if not scan_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scan run found for this organization",
        )

    result = celery_app.send_task(
        "app.tasks.run_verified_portscan.run_verified_portscan",
        args=[str(org.id), str(scan_run.id)],
        queue="verified",
    )

    return PortscanResponse(
        status="queued",
        scan_run_id=str(scan_run.id),
        task_id=result.id,
    )
