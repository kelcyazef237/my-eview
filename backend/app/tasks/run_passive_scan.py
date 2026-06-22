"""Celery task that runs a passive scan via the orchestrator."""

import asyncio

from app.database import SessionLocal
from app.tasks.celery_app import app


@app.task(bind=True, max_retries=3)
def run_passive_scan(self, org_id: str, is_full_report: bool = False) -> dict:
    """Run a passive scan for an organization.

    Creates a DB session, resolves the org's primary domain, and delegates
    to scan_orchestrator.run_scan.
    """
    from app.models.organization import Organization
    from app.services.scan_orchestrator import run_scan

    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return {"status": "error", "detail": f"Organization {org_id} not found"}
        scan_run = asyncio.run(run_scan(db, org.primary_domain, is_full_report=is_full_report))
        return {
            "status": scan_run.status,
            "scan_run_id": str(scan_run.id),
            "org_id": org_id,
            "is_full_report": is_full_report,
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc
    finally:
        db.close()


@app.task
def dispatch_monitoring_scans() -> dict:
    """Beat-scheduled dispatcher: enqueue a monitoring scan for every org."""
    from app.models.organization import Organization

    db = SessionLocal()
    try:
        orgs = db.query(Organization).all()
        count = 0
        for org in orgs:
            run_passive_scan.delay(str(org.id), is_full_report=False)
            count += 1
        return {"dispatched": count}
    finally:
        db.close()