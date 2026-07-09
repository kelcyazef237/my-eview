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
from app.models.app_setting import AppSetting
from app.models.organization import Organization
from app.models.scan_run import ScanRun
from app.models.score import Score
from app.models.user import User
from app.services.ai_report import (
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    PROVIDER_PRESETS,
    build_scan_summary,
    generate_ai_report,
    get_ai_config,
)
from app.services.scan_orchestrator import run_scan

router = APIRouter()

ASSIGNABLE_ROLES = {UserRole.OWNER.value, UserRole.OWNER_TECHNICAL.value, UserRole.OPS.value}


class ApproveRequest(BaseModel):
    role: str


class UserPatchRequest(BaseModel):
    is_active: bool | None = None
    role: str | None = None
    full_name: str | None = None
    username: str | None = None
    email: str | None = None


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
    """Toggle is_active, change role, or edit profile fields."""
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
    if payload.full_name is not None:
        target.full_name = payload.full_name.strip() or None
    if payload.username is not None:
        new_username = payload.username.strip()
        if new_username:
            existing = db.query(User).filter(
                User.username == new_username,
                User.id != target.id,
            ).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            target.username = new_username
    if payload.email is not None:
        new_email = payload.email.strip().lower()
        if new_email:
            existing = db.query(User).filter(
                User.email == new_email,
                User.id != target.id,
            ).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
            target.email = new_email
        else:
            target.email = None

    db.commit()
    return {
        "id": str(target.id),
        "username": target.username,
        "email": target.email,
        "full_name": target.full_name,
        "role": target.role,
        "is_active": target.is_active,
        "registration_status": target.registration_status,
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Permanently delete a user."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if target.role == UserRole.GLOBAL_ADMIN.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete the global admin")

    db.delete(target)
    db.commit()
    return {"id": user_id, "deleted": True}


@router.get("/orgs")
def list_orgs(
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """List organizations with their latest score.

    Supports optional substring search (name/domain) and pagination via
    `limit`/`offset`. Returns `{items, total}` so the client can show
    "Load more" and total counts.
    """
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    query = db.query(Organization)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            (Organization.name.ilike(like))
            | (Organization.primary_domain.ilike(like))
        )
    total = query.count()
    orgs = query.order_by(Organization.created_at.desc()).offset(offset).limit(limit).all()

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
                "verified_portscan_authorized": o.verified_portscan_authorized,
                "latest_score": latest_score.overall_score if latest_score else None,
                "latest_shield_tier": latest_score.shield_tier if latest_score else None,
                "latest_computed_at": latest_score.computed_at.isoformat() if latest_score else None,
                "created_at": o.created_at.isoformat(),
            }
        )
    return {"items": result, "total": total, "limit": limit, "offset": offset}


class CleanScanDataRequest(BaseModel):
    confirm: str


@router.post("/clean-scan-data")
def clean_scan_data(
    req: CleanScanDataRequest,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Wipe all organizations and their scan data.

    Detaches global admins (sets org_id = NULL) so they survive the cascade,
    then deletes every organization. DB-level CASCADE on Organization
    removes scan_runs, findings, scores, score_history, assets,
    report_shares, and non-global owner/ops users attached to those orgs.
    """
    if req.confirm != "WIPE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation token must be the literal string 'WIPE'",
        )

    # Detach global admins so they aren't cascaded away with their orgs.
    db.query(User).filter(User.role == UserRole.GLOBAL_ADMIN.value).update(
        {User.org_id: None}
    )

    org_count = db.query(Organization).count()
    db.query(Organization).delete()
    db.commit()
    return {
        "status": "wiped",
        "deleted_organizations": org_count,
        "deleted_by": str(user.id),
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }


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


class AdminScanRequest(BaseModel):
    name: str
    domain: str


@router.post("/scan")
async def admin_scan(
    req: AdminScanRequest,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Create or update an organization by name + domain, then run a full scan.

    Unlike the public lookup (which creates an org with name=domain and a
    partial report), this is the admin onboarding path: the organization is
    registered with its real name, and the scan produces a full report.
    If the domain already exists, the org name is updated to the provided
    value (so reports speak about the institution, not the domain).
    """
    domain = req.domain.lower().strip()
    name = req.name.strip()
    if not domain or not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both organization name and domain are required.",
        )

    org = db.query(Organization).filter(Organization.primary_domain == domain).first()
    if org:
        if org.name != name:
            org.name = name
            db.commit()
            db.refresh(org)
    else:
        org = Organization(name=name, primary_domain=domain, country="CM")
        db.add(org)
        db.commit()
        db.refresh(org)

    scan_run = await run_scan(db, domain, is_full_report=True)
    return {
        "scan_run_id": str(scan_run.id),
        "status": scan_run.status,
        "org_id": str(org.id),
        "name": org.name,
        "domain": org.primary_domain,
    }


class PortscanAuthRequest(BaseModel):
    authorized: bool


@router.patch("/orgs/{org_id}/portscan-auth")
def toggle_portscan_auth(
    org_id: str,
    payload: PortscanAuthRequest,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Authorize or revoke verified port-scan access for an organization."""
    from datetime import datetime, timezone
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    org.verified_portscan_authorized = payload.authorized
    org.verified_portscan_authorized_at = datetime.now(timezone.utc) if payload.authorized else None
    db.commit()
    return {
        "id": str(org.id),
        "domain": org.primary_domain,
        "verified_portscan_authorized": org.verified_portscan_authorized,
    }


# ===== AI REPORT SETTINGS =====

class AISettingsRequest(BaseModel):
    api_key: str
    provider: str | None = None
    endpoint: str | None = None
    model: str | None = None


@router.get("/ai-settings")
def get_ai_settings(
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Read the AI report config. The API key is masked for safety."""
    config = get_ai_config(db)
    key = config.get("api_key")
    provider = config.get("provider") or DEFAULT_PROVIDER
    preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS[DEFAULT_PROVIDER])
    return {
        "has_key": bool(key),
        "api_key_masked": (key[:4] + "…" + key[-4:]) if key else None,
        "provider": provider,
        "endpoint": config.get("endpoint") or preset["endpoint"],
        "model": config.get("model") or preset["model"],
        "providers": list(PROVIDER_PRESETS.keys()),
    }


@router.post("/ai-settings")
def set_ai_settings(
    req: AISettingsRequest,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Store the AI API key + provider + endpoint + model in app_settings.

    The key is never returned in full by the GET endpoint and is never
    committed to the repo. Updating overwrites the previous value.

    When a `provider` is supplied ("deepseek" or "ollama"), the
    endpoint/model are reset to that provider's preset unless the caller
    also passes explicit endpoint/model overrides.
    """
    provider = (req.provider or DEFAULT_PROVIDER).lower()
    if provider not in PROVIDER_PRESETS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider must be one of: {', '.join(sorted(PROVIDER_PRESETS))}",
        )
    preset = PROVIDER_PRESETS[provider]
    endpoint = req.endpoint or preset["endpoint"]
    model = req.model or preset["model"]

    for k, v in {
        "ai_api_key": req.api_key,
        "ai_provider": provider,
        "ai_endpoint": endpoint,
        "ai_model": model,
    }.items():
        row = db.query(AppSetting).filter(AppSetting.key == k).first()
        if row:
            row.value = v
            row.updated_by = user.id
            row.updated_at = datetime.now(timezone.utc)
        else:
            db.add(AppSetting(key=k, value=v, updated_by=user.id))
    db.commit()
    return {"status": "saved", "provider": provider, "endpoint": endpoint, "model": model}


@router.get("/scan-runs/{scan_run_id}/ai-summary")
def ai_scan_summary(
    scan_run_id: str,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Preview the JSON summary that would be sent to the LLM.

    Useful for debugging what the AI actually sees without spending a
    provider call.
    """
    run = db.query(ScanRun).filter(ScanRun.id == scan_run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan run not found")
    return build_scan_summary(db, scan_run_id)


@router.post("/scan-runs/{scan_run_id}/ai-report")
def ai_report_generate(
    scan_run_id: str,
    user: User = Depends(require_global_admin),
    db: Session = Depends(get_db),
):
    """Generate an AI-assisted report for a scan run.

    Assembles the scan evidence, calls GLM-4.7-Flash with it, and
    returns the model's structured assessment (tier, outlook, risk
    narratives, hygiene, exec summary, conclusion). The frontend can
    then render it via the same template or display the raw JSON.
    """
    run = db.query(ScanRun).filter(ScanRun.id == scan_run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan run not found")
    if not run.score:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scan has no score yet")
    try:
        result = generate_ai_report(db, scan_run_id)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    return result