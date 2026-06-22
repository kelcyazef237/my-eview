"""Gated verified-tier light port-scan task.

Runs only when the organization has explicitly opted into the verified port-scan
tier. The task persists raw evidence and a ``legacy_service`` vector finding, then
re-scores the associated scan run so the new state is reflected in the published
score, shield tier, and TIA output.
"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.collectors import portscan_collector
from app.constants import ScanStatus, VectorState
from app.database import SessionLocal
from app.models.asset import Asset
from app.models.category_score import CategoryScore
from app.models.organization import Organization
from app.models.raw_evidence import RawEvidence
from app.models.scan_run import ScanRun
from app.models.score import Score
from app.models.score_history import ScoreHistory
from app.models.tia_entry import TiaEntry
from app.models.vector_finding import VectorFinding
from app.normalization.normalize_portscan import normalize_legacy_service
from app.reference_data import CATEGORY_ROWS, VECTOR_ROWS
from app.scoring.engine import score_run
from app.scoring.outlook_mapper import outlook_for_score
from app.scoring.shield_mapper import shield_for_score
from app.tia.template_engine import TemplateEngine
from app.tasks.celery_app import app

LEGACY_SERVICE_KEY = "legacy_service"


def _to_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value) if isinstance(value, str) else value


def _build_findings_from_scan_run(db: Session, scan_run: ScanRun) -> dict[str, dict[str, Any]]:
    """Build a normalized findings dict from persisted vector findings."""
    findings: dict[str, dict[str, Any]] = {}
    for vf in scan_run.vector_findings:
        if not vf.vector:
            continue
        findings[vf.vector.key] = {
            "state": vf.state,
            "meta": vf.evidence_ref,
        }
    return findings


def _persist_or_update_finding(
    db: Session,
    scan_run_id: uuid.UUID,
    asset_id: uuid.UUID,
    vector_key: str,
    finding: dict[str, Any],
) -> None:
    vec_key_to_id = {v["key"]: v["id"] for v in VECTOR_ROWS}
    vector_id = vec_key_to_id.get(vector_key)
    if not vector_id:
        raise ValueError(f"Unknown vector key: {vector_key}")

    existing = (
        db.query(VectorFinding)
        .filter_by(scan_run_id=scan_run_id, vector_id=vector_id)
        .first()
    )
    meta = finding.get("meta")
    evidence_ref = str(meta) if meta is not None else None
    if existing:
        existing.state = finding.get("state", VectorState.NOT_OBSERVED.value)
        existing.evidence_ref = evidence_ref
        existing.asset_id = asset_id
    else:
        db.add(VectorFinding(
            scan_run_id=scan_run_id,
            asset_id=asset_id,
            vector_id=vector_id,
            state=finding.get("state", VectorState.NOT_OBSERVED.value),
            evidence_ref=evidence_ref,
        ))


def _rescore_scan_run(db: Session, scan_run: ScanRun, domain: str) -> dict[str, Any]:
    """Re-score a scan run after a finding has been updated.

    Returns a status dict for the Celery task result.
    """
    findings = _build_findings_from_scan_run(db, scan_run)
    score_result = score_run(findings)

    scan_run.status = ScanStatus.COMPLETE.value if score_result.is_complete else ScanStatus.INCOMPLETE.value
    scan_run.finished_at = datetime.now(timezone.utc)
    db.commit()

    if not score_result.is_complete:
        return {"status": "incomplete", "reason": "too_many_not_observed"}

    org = scan_run.organization
    shield = shield_for_score(score_result.overall_score)

    previous_full = (
        db.query(Score)
        .filter_by(org_id=org.id, is_full_report=True)
        .order_by(Score.computed_at.desc())
        .first()
    )
    previous_score = previous_full.overall_score if previous_full else None
    is_first_full_report = scan_run.is_full_report and previous_full is None
    outlook = outlook_for_score(
        score_result.overall_score,
        shield.tier,
        previous_score,
        is_first_full_report=is_first_full_report,
    )

    # Replace category scores.
    db.query(CategoryScore).filter_by(scan_run_id=scan_run.id).delete()
    cat_key_to_id = {c["key"]: c["id"] for c in CATEGORY_ROWS}
    for cat_key, cat_score in score_result.category_scores.items():
        cat_id = cat_key_to_id.get(cat_key)
        if cat_id is None:
            continue
        db.add(CategoryScore(
            scan_run_id=scan_run.id,
            category_id=cat_id,
            points_lost=cat_score["points_lost"],
            points_remaining=cat_score["points_remaining"],
        ))

    # Replace TIA entries.
    cat_key_by_id = {c["id"]: c["key"] for c in CATEGORY_ROWS}
    category_vector_states: dict[str, dict[str, dict]] = {}
    for vec_key, finding in findings.items():
        vec = next((v for v in VECTOR_ROWS if v["key"] == vec_key), None)
        if not vec:
            continue
        cat_key = cat_key_by_id.get(vec["category_id"])
        if cat_key:
            category_vector_states.setdefault(cat_key, {})[vec_key] = finding

    engine = TemplateEngine()
    tia_results = engine.render_all(org.name, domain, category_vector_states)
    db.query(TiaEntry).filter_by(scan_run_id=scan_run.id).delete()
    for cat_key, tia in tia_results.items():
        cat_id = cat_key_to_id.get(cat_key)
        if cat_id is None:
            continue
        db.add(TiaEntry(
            scan_run_id=scan_run.id,
            category_id=cat_id,
            template_id=tia["template_id"],
            rendered_text=tia["rendered_text"],
        ))

    # Upsert score record.
    score_record = db.query(Score).filter_by(scan_run_id=scan_run.id).first()
    if score_record:
        score_record.overall_score = score_result.overall_score
        score_record.shield_tier = shield.tier
        score_record.outlook = outlook.outlook
        score_record.computed_at = datetime.now(timezone.utc)
    else:
        score_record = Score(
            scan_run_id=scan_run.id,
            org_id=org.id,
            overall_score=score_result.overall_score,
            shield_tier=shield.tier,
            outlook=outlook.outlook,
            is_full_report=scan_run.is_full_report,
            previous_full_report_id=previous_full.id if previous_full else None,
        )
        db.add(score_record)
        db.add(ScoreHistory(
            org_id=org.id,
            scan_run_id=scan_run.id,
            overall_score=score_result.overall_score,
            is_full_report=scan_run.is_full_report,
        ))

    db.commit()
    return {
        "status": "complete",
        "overall_score": score_result.overall_score,
        "shield_tier": shield.tier,
        "outlook": outlook.outlook,
    }


@app.task(bind=True, queue="verified", max_retries=2, default_retry_delay=30)
def run_verified_portscan(self, org_id: str, scan_run_id: str) -> dict:
    """Run the gated legacy-port scan for a verified organization.

    Args:
        org_id: Organization UUID as string.
        scan_run_id: ScanRun UUID as string.

    Returns:
        dict with ``status`` and scoring details (if complete).
    """
    db = SessionLocal()
    try:
        org_uuid = _to_uuid(org_id)
        scan_uuid = _to_uuid(scan_run_id)

        org = db.query(Organization).filter_by(id=org_uuid).first()
        if not org:
            return {"status": "failed", "reason": "organization_not_found"}

        scan_run = db.query(ScanRun).filter_by(id=scan_uuid, org_id=org_uuid).first()
        if not scan_run:
            return {"status": "failed", "reason": "scan_run_not_found"}

        if not org.verified_portscan_authorized:
            return {
                "status": "skipped",
                "reason": "verified_portscan_not_authorized",
                "org_id": str(org.id),
                "scan_run_id": str(scan_run.id),
            }

        domain = org.primary_domain
        primary_asset = (
            db.query(Asset)
            .filter_by(org_id=org.id, type="domain", value=domain.lower())
            .first()
        )
        if not primary_asset:
            primary_asset = Asset(
                org_id=org.id,
                type="domain",
                value=domain.lower(),
                discovered_via="primary",
            )
            db.add(primary_asset)
            db.commit()
            db.refresh(primary_asset)

        evidence = asyncio.run(portscan_collector.collect(domain))

        db.add(RawEvidence(
            scan_run_id=scan_run.id,
            asset_id=primary_asset.id,
            collector_name="verified_portscan",
            raw_payload=evidence,
            attempt_count=evidence.get("attempts", 1),
        ))
        db.commit()

        finding = normalize_legacy_service(evidence)
        _persist_or_update_finding(
            db,
            scan_run.id,
            primary_asset.id,
            LEGACY_SERVICE_KEY,
            finding,
        )
        db.commit()

        # If the parent scan is still running, leave the finding in place without
        # scoring; the orchestrator will pick it up and score once it finishes.
        if scan_run.status == ScanStatus.RUNNING.value:
            return {
                "status": "pending_parent_scan",
                "org_id": str(org.id),
                "scan_run_id": str(scan_run.id),
                "legacy_service_state": finding["state"],
            }

        return _rescore_scan_run(db, scan_run, domain)
    except Exception as exc:
        db.rollback()
        # Celery will retry on transient failures; hard failures surface here.
        raise self.retry(exc=exc)
    finally:
        db.close()
