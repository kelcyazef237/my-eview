"""Global admin router — oversight of users, registrations, orgs, and scan runs.

All endpoints require the `global_admin` role (Kelcy). Global admin also passes
every other role gate, so these endpoints are in addition to (not instead of)
the owner/ops endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import require_global_admin
from app.constants import UserRole
from app.database import get_db
from app.models.organization import Organization
from app.models.scan_run import ScanRun
from app.models.score import Score
from app.models.user import User
from app.services.scan_orchestrator import run_scan

router = APIRouter()

ASSIGNABLE_ROLES = {UserRole.OWNER.value, UserRole.OWNER_TECHNICAL.value, UserRole.OPS.value}


class ApproveRequest(BaseModel):
    role: str


class UserPatchRequest(BaseModel):
    is_active: bool | None = None
    role: str | None = None


@router.get("/metrics")
def metrics(user: User = Depends(require_global_admin), db: Session = Depends(get_db)):
    """System-wide counts for the admin dashboard tiles."""
    return {
        "total_orgs": db.query(Organization).count(),
        "total_users": db.query(User).count(),
        "total_scans": db.query(ScanRun).count(),
        "pending_registrations": db.query(User).filter(User.registration_status == "pending").count(),
    }


@router.get("/registrations")
def list_registrations(user: User = Depends(require_global_admin), db: Session = Depends(get_db)):
    """List users awaiting admin validation."""
    pending = (
        db.query(User)
        .filter(User.registration_status == "pending")
        .order_by(User.created_at.desc())
        .all()
    )
    return [
        {
            "id": str(u.id),
            "full_name": u.full_name,
            "username": u.username,
            "email": u.email,
            "organization_domain": u.organization.primary_domain if u.organization else None,
            "organization_name": u.organization.name if u.organization else None,
            "created_at": u.created_at.isoformat(),
        }
        for u in pending
    ]


@router.post("/registrations/{user_id}/approve")
def approve_registration(
    user_id: str,
    payload: ApproveRequest,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Approve a pending registration and assign a role."""
    if payload.role not in ASSIGNABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of: {', '.join(sorted(ASSIGNABLE_ROLES))}",
        )
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.registration_status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not pending validation")

    target.role = payload.role
    target.registration_status = "approved"
    target.is_active = True
    db.commit()
    return {
        "id": str(target.id),
        "username": target.username,
        "full_name": target.full_name,
        "role": target.role,
        "registration_status": target.registration_status,
        "is_active": target.is_active,
    }


@router.post("/registrations/{user_id}/reject")
def reject_registration(
    user_id: str,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Reject a pending registration."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.registration_status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not pending validation")

    target.registration_status = "rejected"
    target.is_active = False
    db.commit()
    return {"id": str(target.id), "registration_status": target.registration_status}


@router.get("/users")
def list_users(
    status_filter: str | None = None,
    role_filter: str | None = None,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """List all users with their role, status, org, and last login."""
    q = db.query(User)
    if status_filter:
        q = q.filter(User.registration_status == status_filter)
    if role_filter:
        q = q.filter(User.role == role_filter)
    users = q.order_by(User.created_at.desc()).all()
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "registration_status": u.registration_status,
            "is_active": u.is_active,
            "organization_domain": u.organization.primary_domain if u.organization else None,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat(),
        }
        for u in users
    ]


@router.patch("/users/{user_id}")
def update_user(
    user_id: str,
    payload: UserPatchRequest,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Toggle is_active or change a user's role."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.role == UserRole.GLOBAL_ADMIN.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot modify the global admin")

    if payload.role is not None:
        if payload.role not in ASSIGNABLE_ROLES and payload.role != UserRole.PUBLIC.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role must be one of: {', '.join(sorted(ASSIGNABLE_ROLES | {UserRole.PUBLIC.value}))}",
            )
        target.role = payload.role
    if payload.is_active is not None:
        target.is_active = payload.is_active

    db.commit()
    return {
        "id": str(target.id),
        "username": target.username,
        "role": target.role,
        "is_active": target.is_active,
        "registration_status": target.registration_status,
    }


@router.get("/orgs")
def list_orgs(user: User = Depends(require_global_admin), db: Session = Depends(get_db)):
    """List all organizations with their latest score."""
    orgs = db.query(Organization).order_by(Organization.created_at.desc()).all()
    result = []
    for o in orgs:
        latest_score = (
            db.query(Score)
            .filter(Score.org_id == o.id)
            .order_by(Score.computed_at.desc())
            .first()
        )
        result.append(
            {
                "id": str(o.id),
                "name": o.name,
                "domain": o.primary_domain,
                "ownership_verified": o.ownership_verified,
                "latest_score": latest_score.overall_score if latest_score else None,
                "latest_shield_tier": latest_score.shield_tier if latest_score else None,
                "latest_computed_at": latest_score.computed_at.isoformat() if latest_score else None,
                "created_at": o.created_at.isoformat(),
            }
        )
    return result


@router.get("/scan-runs")
def list_scan_runs(user: User = Depends(require_global_admin), db: Session = Depends(get_db)):
    """List the 50 most recent scan runs across all orgs."""
    runs = db.query(ScanRun).order_by(ScanRun.started_at.desc()).limit(50).all()
    return [
        {
            "id": str(r.id),
            "org_id": str(r.org_id),
            "domain": r.organization.primary_domain,
            "status": r.status,
            "is_full_report": r.is_full_report,
            "overall_score": r.score.overall_score if r.score else None,
            "shield_tier": r.score.shield_tier if r.score else None,
            "started_at": r.started_at.isoformat(),
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
        }
        for r in runs
    ]


@router.post("/rescan/{org_id}")
async def admin_rescan(
    org_id: str,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Trigger a passive rescan for any organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    scan_run = await run_scan(db, org.primary_domain, is_full_report=False)
    return {"scan_run_id": str(scan_run.id), "status": scan_run.status, "domain": org.primary_domain}