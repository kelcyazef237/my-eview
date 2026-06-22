"""End-to-end passive scan orchestrator."""

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.constants import ScanStatus, UserRole
from app.collectors import asset_discovery, dns_collector, http_collector, tls_collector, threat_intel_collector, whois_collector
from app.database import Base
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
from app.normalization import normalize_asset_surface, normalize_dns, normalize_http, normalize_threat, normalize_tls, normalize_whois
from app.reference_data import CATEGORY_ROWS, VECTOR_ROWS
from app.scoring.engine import score_run
from app.scoring.outlook_mapper import outlook_for_score
from app.scoring.shield_mapper import shield_for_score
from app.tia.template_engine import TemplateEngine


async def run_scan(db: Session, domain: str, is_full_report: bool = False) -> ScanRun:
    # Get or create organization
    org = db.query(Organization).filter(Organization.primary_domain == domain.lower()).first()
    if not org:
        org = Organization(
            name=domain,
            primary_domain=domain.lower(),
            country="CM",
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    # Ensure a primary asset exists
    primary_asset = db.query(Asset).filter_by(org_id=org.id, type="domain", value=domain.lower()).first()
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

    scan_run = ScanRun(
        org_id=org.id,
        status=ScanStatus.RUNNING.value,
        is_full_report=is_full_report,
    )
    db.add(scan_run)
    db.commit()
    db.refresh(scan_run)

    # Run passive collectors concurrently
    dns_evidence, whois_evidence, tls_evidence, http_evidence, discovery_evidence = await asyncio.gather(
        dns_collector.collect(domain),
        whois_collector.collect(domain),
        tls_collector.collect(domain),
        http_collector.collect(domain),
        asset_discovery.discover(domain),
        return_exceptions=True,
    )

    def _unwrap(result):
        if isinstance(result, Exception):
            return {"error": str(result)}
        return result

    dns_evidence = _unwrap(dns_evidence)
    whois_evidence = _unwrap(whois_evidence)
    tls_evidence = _unwrap(tls_evidence)
    http_evidence = _unwrap(http_evidence)
    discovery_evidence = _unwrap(discovery_evidence)

    # Threat intel (uses DB session for cache lookups; async wrapper handles the sync calls)
    threat_evidence = await threat_intel_collector.collect(domain, db)

    # Store raw evidence
    evidence_records = [
        ("dns", dns_evidence, primary_asset.id),
        ("whois", whois_evidence, primary_asset.id),
        ("tls", tls_evidence, primary_asset.id),
        ("http", http_evidence, primary_asset.id),
        ("asset_discovery", discovery_evidence, primary_asset.id),
        ("threat_intel", threat_evidence, primary_asset.id),
    ]
    for collector_name, payload, asset_id in evidence_records:
        db.add(RawEvidence(
            scan_run_id=scan_run.id,
            asset_id=asset_id,
            collector_name=collector_name,
            raw_payload=payload,
            attempt_count=payload.get("attempts", 1),
        ))
    db.commit()

    # Re-run TLS and HTTP collectors against discovered subdomains for
    # unmanaged-asset indicator detection (cert-issuer mismatch, stale banners).
    subdomain_results: list[dict] = []
    discovered = discovery_evidence.get("discovered_assets") or []
    # Limit to 20 subdomains to stay within scan-time budget.
    for sub in discovered[:20]:
        if sub == domain.lower():
            continue
        sub_asset = db.query(Asset).filter_by(org_id=org.id, type="subdomain", value=sub).first()
        if not sub_asset:
            sub_asset = Asset(
                org_id=org.id,
                type="subdomain",
                value=sub,
                discovered_via="ct_logs",
            )
            db.add(sub_asset)
            db.commit()
            db.refresh(sub_asset)

        sub_tls, sub_http = await asyncio.gather(
            tls_collector.collect(sub),
            http_collector.collect(sub),
            return_exceptions=True,
        )
        sub_tls = _unwrap(sub_tls)
        sub_http = _unwrap(sub_http)

        # Store subdomain raw evidence
        db.add(RawEvidence(
            scan_run_id=scan_run.id, asset_id=sub_asset.id,
            collector_name="tls", raw_payload=sub_tls,
            attempt_count=sub_tls.get("attempts", 1),
        ))
        db.add(RawEvidence(
            scan_run_id=scan_run.id, asset_id=sub_asset.id,
            collector_name="http", raw_payload=sub_http,
            attempt_count=sub_http.get("attempts", 1),
        ))
        subdomain_results.append({"subdomain": sub, "tls": sub_tls, "http": sub_http})
    db.commit()

    # Normalize
    findings: dict[str, dict[str, Any]] = {}
    findings.update(normalize_dns(dns_evidence))
    findings.update(normalize_whois(whois_evidence))
    findings.update(normalize_tls(tls_evidence))
    findings.update(normalize_http(http_evidence))
    findings.update(normalize_threat(threat_evidence))
    findings.update(normalize_asset_surface(discovery_evidence, tls_evidence, http_evidence, subdomain_results))

    # Legacy service exposure defaults to NOT_APPLICABLE unless verified tier enabled.
    if not org.verified_portscan_authorized:
        from app.constants import VectorState
        findings["legacy_service"] = {"state": VectorState.NOT_APPLICABLE.value}

    # Persist vector findings with evidence reference to raw_evidence collector name
    vec_key_to_id = {v["key"]: v["id"] for v in VECTOR_ROWS}
    # Map vector keys to the collector that produced their evidence
    vec_to_collector = {
        "spf_presence": "dns", "dkim_presence": "dns", "dmarc_enforcement": "dns",
        "dnssec_adoption": "dns",
        "domain_age": "whois", "domain_expiration": "whois",
        "tls_version": "tls", "certificate_health": "tls",
        "security_headers": "http", "https_enforcement": "http",
        "exposed_admin": "http", "tech_obsolescence": "http",
        "software_version": "http", "sri_adoption": "http",
        "malware": "threat_intel", "phishing": "threat_intel",
        "spam_blacklist": "threat_intel", "botnet": "threat_intel",
        "blacklist_aggregate": "threat_intel",
        "asset_count": "asset_discovery", "shadow_assets": "asset_discovery",
        "unmanaged_assets": "asset_discovery",
        "legacy_service": "portscan",
    }
    for vec_key, finding in findings.items():
        vec_id = vec_key_to_id.get(vec_key)
        if vec_id:
            db.add(VectorFinding(
                scan_run_id=scan_run.id,
                asset_id=primary_asset.id,
                vector_id=vec_id,
                state=finding.get("state", "NOT_OBSERVED"),
                evidence_ref=vec_to_collector.get(vec_key, "unknown"),
            ))
    db.commit()

    # Score
    score_result = score_run(findings)

    scan_run.status = ScanStatus.COMPLETE.value if score_result.is_complete else ScanStatus.INCOMPLETE.value
    scan_run.finished_at = datetime.now(timezone.utc)
    db.commit()

    # Even if the scan is incomplete (too many NOT_OBSERVED vectors), we still
    # create a Score record so the user gets a result.  The scan_run.status
    # captures the incompleteness — the API can surface a warning.
    shield = shield_for_score(score_result.overall_score)

    # Previous full report for outlook
    previous_full = (
        db.query(Score)
        .filter_by(org_id=org.id, is_full_report=True)
        .order_by(Score.computed_at.desc())
        .first()
    )
    previous_score = previous_full.overall_score if previous_full else None
    is_first_full_report = is_full_report and previous_full is None
    outlook = outlook_for_score(
        score_result.overall_score,
        shield.tier,
        previous_score,
        is_first_full_report=is_first_full_report,
    )

    # Persist category scores
    for cat_key, cat_score in score_result.category_scores.items():
        cat_id = next(c["id"] for c in CATEGORY_ROWS if c["key"] == cat_key)
        db.add(CategoryScore(
            scan_run_id=scan_run.id,
            category_id=cat_id,
            points_lost=cat_score["points_lost"],
            points_remaining=cat_score["points_remaining"],
        ))

    score_record = Score(
        scan_run_id=scan_run.id,
        org_id=org.id,
        overall_score=score_result.overall_score,
        shield_tier=shield.tier,
        outlook=outlook.outlook,
        is_full_report=is_full_report,
        previous_full_report_id=previous_full.id if previous_full else None,
    )
    db.add(score_record)

    db.add(ScoreHistory(
        org_id=org.id,
        scan_run_id=scan_run.id,
        overall_score=score_result.overall_score,
        is_full_report=is_full_report,
    ))

    # TIA
    category_vector_states: dict[str, dict[str, dict]] = {}
    cat_key_by_id = {c["id"]: c["key"] for c in CATEGORY_ROWS}
    for vec_key, finding in findings.items():
        vec = next((v for v in VECTOR_ROWS if v["key"] == vec_key), None)
        if not vec:
            continue
        cat_key = cat_key_by_id[vec["category_id"]]
        category_vector_states.setdefault(cat_key, {})[vec_key] = finding

    engine = TemplateEngine()
    tia_results = engine.render_all(org.name, domain, category_vector_states)
    for cat_key, tia in tia_results.items():
        cat_id = next(c["id"] for c in CATEGORY_ROWS if c["key"] == cat_key)
        db.add(TiaEntry(
            scan_run_id=scan_run.id,
            category_id=cat_id,
            template_id=tia["template_id"],
            rendered_text=tia["rendered_text"],
        ))

    db.commit()

    # For verified-tier organizations, enqueue the gated port-scan on a
    # dedicated queue so it never blocks passive scans. The Celery task will
    # re-score the run once the port-scan evidence is collected.
    if org.verified_portscan_authorized:
        from app.tasks.celery_app import app as celery_app
        celery_app.send_task(
            "app.tasks.run_verified_portscan.run_verified_portscan",
            args=[str(org.id), str(scan_run.id)],
            queue="verified",
        )

    return scan_run
