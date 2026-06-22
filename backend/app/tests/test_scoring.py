import pytest

from app.constants import VectorState
from app.scoring.engine import score_run
from app.scoring.rules_loader import load_ruleset, validate_ruleset


def test_ruleset_validates():
    ruleset = load_ruleset()
    validate_ruleset(ruleset)


def test_perfect_score():
    ruleset = load_ruleset()
    findings = {
        vec["key"]: {"state": "PASS"}
        for cat in ruleset["categories"]
        for vec in cat["vectors"]
        if cat["scored"]
    }
    # DMARC needs policy meta for PASS
    findings["dmarc_enforcement"] = {"state": "PASS", "meta": {"dmarc_policy": "reject"}}
    # Threat-intel vectors need activity meta
    for key in ("malware", "phishing", "botnet"):
        findings[key] = {"state": "PASS", "meta": {"activity": "none"}}

    result = score_run(findings, ruleset)
    assert result.overall_score == 1000
    assert result.is_complete is True
    assert result.not_observed_count == 0


def test_dmarc_none_deduction():
    ruleset = load_ruleset()
    findings = {
        "spf_presence": {"state": "PASS"},
        "dkim_presence": {"state": "PASS"},
        "dmarc_enforcement": {"state": "WARN", "meta": {"dmarc_policy": "none"}},
    }
    # All other vectors PASS with appropriate meta
    for cat in ruleset["categories"]:
        if not cat["scored"]:
            continue
        for vec in cat["vectors"]:
            if vec["key"] in findings:
                continue
            meta = {}
            if vec["key"] in ("malware", "phishing", "botnet"):
                meta = {"activity": "none"}
            findings[vec["key"]] = {"state": "PASS", "meta": meta}

    result = score_run(findings, ruleset)
    assert result.category_scores["email_trust"]["points_lost"] == 60
    assert result.category_scores["email_trust"]["points_remaining"] == 80


def test_incomplete_run_when_too_many_not_observed():
    ruleset = load_ruleset()
    findings = {
        vec["key"]: {"state": "NOT_OBSERVED"}
        for cat in ruleset["categories"]
        for vec in cat["vectors"]
        if cat["scored"]
    }
    result = score_run(findings, ruleset)
    assert result.not_observed_ratio > 0.15
    assert result.is_complete is False


def test_category_floor_at_zero():
    ruleset = load_ruleset()
    findings = {
        "spf_presence": {"state": "FAIL"},
        "dkim_presence": {"state": "FAIL"},
        "dmarc_enforcement": {"state": "FAIL"},
    }
    result = score_run(findings, ruleset)
    assert result.category_scores["email_trust"]["points_remaining"] == 0


def test_determinism():
    ruleset = load_ruleset()
    findings = {
        "spf_presence": {"state": "FAIL"},
        "dkim_presence": {"state": "PASS"},
        "dmarc_enforcement": {"state": "WARN", "meta": {"dmarc_policy": "quarantine"}},
    }
    for cat in ruleset["categories"]:
        if not cat["scored"]:
            continue
        for vec in cat["vectors"]:
            if vec["key"] in findings:
                continue
            meta = {}
            if vec["key"] in ("malware", "phishing", "botnet"):
                meta = {"activity": "none"}
            findings[vec["key"]] = {"state": "PASS", "meta": meta}

    r1 = score_run(findings, ruleset)
    r2 = score_run(findings, ruleset)
    assert r1 == r2


def test_not_observed_never_scored_as_fail():
    """NOT_OBSERVED must not produce a deduction, even for meta-based vectors like DMARC.

    Before the fix, DMARC NOT_OBSERVED fell through to `match: true` with -80 deduction,
    silently scoring a failed check as FAIL. This test guards against regression.
    """
    ruleset = load_ruleset()
    findings = {
        vec["key"]: {"state": "PASS"}
        for cat in ruleset["categories"]
        for vec in cat["vectors"]
        if cat["scored"]
    }
    # Override DMARC to NOT_OBSERVED (check couldn't run)
    findings["dmarc_enforcement"] = {"state": "NOT_OBSERVED"}
    # Other meta-based vectors need activity meta for PASS
    for key in ("malware", "phishing", "botnet"):
        findings[key] = {"state": "PASS", "meta": {"activity": "none"}}

    result = score_run(findings, ruleset)
    # DMARC NOT_OBSERVED must contribute 0 deduction, not -80
    assert result.category_scores["email_trust"]["points_lost"] == 0
    assert result.overall_score == 1000


def test_single_not_observed_does_not_invalidate_run():
    """A single NOT_OBSERVED among many PASS vectors should not mark the run incomplete."""
    ruleset = load_ruleset()
    findings = {
        vec["key"]: {"state": "PASS"}
        for cat in ruleset["categories"]
        for vec in cat["vectors"]
        if cat["scored"]
    }
    findings["dmarc_enforcement"] = {"state": "NOT_OBSERVED"}
    for key in ("malware", "phishing", "botnet"):
        findings[key] = {"state": "PASS", "meta": {"activity": "none"}}

    result = score_run(findings, ruleset)
    assert result.not_observed_count == 1
    assert result.is_complete is True
