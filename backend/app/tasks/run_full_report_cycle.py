"""Celery task that triggers a full-report scan cycle for an organization."""

import asyncio

from app.database import SessionLocal
from app.tasks.celery_app import app


@app.task(bind=True)
def run_full_report_cycle(self, org_id: str) -> dict:
    """Run a full-report scan for an organization.

    This produces a formal Full Report snapshot that feeds the outlook
    comparison logic. Monitoring scans (run_passive_scan with is_full_report=False)
    run on a more frequent schedule for internal alerting only.
    """
    from app.models.organization import Organization
    from app.services.scan_orchestrator import run_scan

    db = SessionLocal()
    try:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return {"status": "error", "detail": f"Organization {org_id} not found"}
        scan_run = asyncio.run(run_scan(db, org.primary_domain, is_full_report=True))
        return {
            "status": scan_run.status,
            "scan_run_id": str(scan_run.id),
            "org_id": org_id,
            "is_full_report": True,
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120) from exc
    finally:
        db.close()


@app.task
def dispatch_full_report_cycles() -> dict:
    """Beat-scheduled dispatcher: enqueue a full-report scan for every org."""
    from app.models.organization import Organization

    db = SessionLocal()
    try:
        orgs = db.query(Organization).all()
        count = 0
        for org in orgs:
            run_full_report_cycle.delay(str(org.id))
            count += 1
        return {"dispatched": count}
    finally:
        db.close()