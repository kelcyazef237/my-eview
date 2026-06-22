from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import require_owner_technical
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
    user: User = Depends(require_owner_technical),
    db: Session = Depends(get_db),
):
    """Trigger the gated verified-tier port-scan for the current organization.

    The organization must have ``verified_portscan_authorized`` set to ``True``.
    The task runs on the dedicated ``verified`` Celery queue and re-scores the
    most recent scan run once the port-scan evidence is collected.
    """
    if not user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with an organization",
        )

    org = db.query(Organization).filter(Organization.id == user.org_id).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if not org.verified_portscan_authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verified port-scan not authorized for this organization",
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
