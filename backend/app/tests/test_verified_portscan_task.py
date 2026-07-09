"""Offline unit tests for the verified port-scan Celery task."""

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.constants import ScanStatus, VectorState
from app.reference_data import CATEGORY_ROWS, VECTOR_ROWS
from app.scoring.engine import score_run
from app.tasks.run_verified_portscan import (
    LEGACY_SERVICE_KEY,
    _build_findings_from_scan_run,
    _persist_or_update_finding,
    _rescore_scan_run,
    run_verified_portscan,
)


def _make_vector_finding(vector_key: str, state: str, evidence_ref: dict | None = None):
    vector = SimpleNamespace(key=vector_key)
    return SimpleNamespace(
        vector=vector,
        state=state,
        evidence_ref=evidence_ref,
    )


def test_build_findings_from_scan_run():
    scan_run = SimpleNamespace(
        vector_findings=[
            _make_vector_finding("spf_presence", VectorState.PASS.value),
            _make_vector_finding("legacy_service", VectorState.FAIL.value, {"exposed_ports": [23]}),
        ]
    )
    findings = _build_findings_from_scan_run(MagicMock(), scan_run)
    assert findings["spf_presence"]["state"] == VectorState.PASS.value
    assert findings["legacy_service"]["state"] == VectorState.FAIL.value
    assert findings["legacy_service"]["meta"] == {"exposed_ports": [23]}


def test_persist_or_update_finding_creates_new():
    db = MagicMock()
    db.query().filter_by().first.return_value = None
    vec_key_to_id = {v["key"]: v["id"] for v in VECTOR_ROWS}

    _persist_or_update_finding(
        db,
        uuid.uuid4(),
        uuid.uuid4(),
        "legacy_service",
        {"state": VectorState.FAIL.value, "meta": {"exposed_ports": [23]}},
    )

    added = db.add.call_args[0][0]
    assert added.vector_id == vec_key_to_id["legacy_service"]
    assert added.state == VectorState.FAIL.value
    assert added.evidence_ref == str({"exposed_ports": [23]})


def test_persist_or_update_finding_updates_existing():
    db = MagicMock()
    existing = MagicMock()
    db.query().filter_by().first.return_value = existing

    _persist_or_update_finding(
        db,
        uuid.uuid4(),
        uuid.uuid4(),
        "legacy_service",
        {"state": VectorState.PASS.value},
    )

    assert existing.state == VectorState.PASS.value
    assert existing.evidence_ref is None
    db.add.assert_not_called()


def _complete_findings():
    """Return a complete PASS findings dict for all 21 scored vectors."""
    findings = {}
    for vec in VECTOR_ROWS:
        cat = next(c for c in CATEGORY_ROWS if c["id"] == vec["category_id"])
        if not cat["scored"]:
            continue
        meta = {}
        if vec["key"] == "dmarc_enforcement":
            meta = {"dmarc_policy": "reject"}
        elif vec["key"] in ("malware", "phishing", "botnet"):
            meta = {"activity": "none"}
        findings[vec["key"]] = {"state": VectorState.PASS.value, "meta": meta}
    return findings


def test_rescore_scan_run_publishes_complete_score():
    org_id = uuid.uuid4()
    scan_run_id = uuid.uuid4()

    org = SimpleNamespace(id=org_id, name="Test Org")
    scan_run = SimpleNamespace(
        id=scan_run_id,
        org_id=org_id,
        organization=org,
        status=ScanStatus.COMPLETE.value,
        is_full_report=True,
        finished_at=None,
        vector_findings=[
            _make_vector_finding(k, v["state"], v.get("meta"))
            for k, v in _complete_findings().items()
        ],
    )

    # Mock DB session.
    db = MagicMock()
    db.query().filter_by().order_by().first.return_value = None  # no previous full report
    db.query().filter_by().first.return_value = None  # no existing score

    result = _rescore_scan_run(db, scan_run, "example.com")

    assert result["status"] == "complete"
    assert result["overall_score"] == 1000
    assert result["shield_tier"] == 5
    assert result["outlook"] == "MYETREND: available after 90 days"

    # Verify category scores were added.
    assert db.add.call_count > 0
    added_scores = [call[0][0] for call in db.add.call_args_list]
    category_score_keys = {c["key"] for c in CATEGORY_ROWS if c["scored"]}
    scored_keys = {s.category_id for s in added_scores if hasattr(s, "points_remaining")}
    assert len(scored_keys) == len(category_score_keys)

    db.commit.assert_called()


def test_rescore_incomplete_run_does_not_publish_score():
    org_id = uuid.uuid4()
    scan_run_id = uuid.uuid4()
    org = SimpleNamespace(id=org_id, name="Test Org")

    # Mark 4 scored vectors NOT_OBSERVED to exceed the 15% threshold (4/21).
    not_observed_vectors = ["spf_presence", "dkim_presence", "dmarc_enforcement", "tls_version"]
    vector_findings = [
        _make_vector_finding(v, VectorState.NOT_OBSERVED.value)
        for v in not_observed_vectors
    ]

    scan_run = SimpleNamespace(
        id=scan_run_id,
        org_id=org_id,
        organization=org,
        status=ScanStatus.COMPLETE.value,
        is_full_report=True,
        finished_at=None,
        vector_findings=vector_findings,
    )

    db = MagicMock()
    db.query().filter_by().order_by().first.return_value = None
    result = _rescore_scan_run(db, scan_run, "example.com")

    assert result["status"] == "incomplete"
    assert result["reason"] == "too_many_not_observed"
    # Should not replace category scores or TIA entries.
    db.query().filter_by().delete.assert_not_called()


def test_run_verified_portscan_skips_unauthorized():
    org_id = uuid.uuid4()
    scan_run_id = uuid.uuid4()

    org = SimpleNamespace(
        id=org_id,
        primary_domain="example.com",
        verified_portscan_authorized=False,
    )
    scan_run = SimpleNamespace(id=scan_run_id, org_id=org_id, status=ScanStatus.COMPLETE.value)

    with patch("app.tasks.run_verified_portscan.SessionLocal") as mock_session_local:
        db = MagicMock()
        mock_session_local.return_value = db
        db.query().filter_by().first.side_effect = [org, scan_run]

        result = run_verified_portscan(str(org_id), str(scan_run_id))

    assert result["status"] == "skipped"
    assert result["reason"] == "verified_portscan_not_authorized"


def test_run_verified_portscan_defers_when_parent_scan_running():
    org_id = uuid.uuid4()
    scan_run_id = uuid.uuid4()
    asset_id = uuid.uuid4()

    org = SimpleNamespace(
        id=org_id,
        primary_domain="example.com",
        verified_portscan_authorized=True,
        name="Test Org",
    )
    asset = SimpleNamespace(id=asset_id, type="domain", value="example.com")
    scan_run = SimpleNamespace(
        id=scan_run_id,
        org_id=org_id,
        status=ScanStatus.RUNNING.value,
        is_full_report=False,
        finished_at=None,
        organization=org,
        vector_findings=[],
    )

    evidence = {
        "host": "example.com",
        "results": [],
        "exposed_count": 0,
        "plaintext_count": 0,
        "exposed_ports": [],
    }

    with patch("app.tasks.run_verified_portscan.SessionLocal") as mock_session_local, \
            patch("app.tasks.run_verified_portscan.portscan_collector.collect", return_value=evidence):
        db = MagicMock()
        mock_session_local.return_value = db
        db.query().filter_by().first.side_effect = [org, scan_run, asset, None]

        result = run_verified_portscan(str(org_id), str(scan_run_id))

    assert result["status"] == "pending_parent_scan"
    assert result["legacy_service_state"] == VectorState.PASS.value
